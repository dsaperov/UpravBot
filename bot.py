import logging

from pony.orm import db_session
from random import randint
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
import handlers
from mail import send_email
from models import UserState, SubscribedUsers
from scheduler import Scheduler


def configure_logging():
    log.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("bot.log", 'w', 'UTF-8')

    stream_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    log.addHandler(stream_handler)
    log.addHandler(file_handler)


class Bot:
    """
    Бот для vk.com, запрашивающий у пользователя показания счетчиков и отправляющий их в управляющую компанию/управдому
    по указанному адресу электронной почты.

    Use python3.9
    """

    def __init__(self, token, group_id, scheduler):
        """
        :param token: секретный токен
        :param group_id: group_id группы vk
        """
        self.vk_session = vk_api.VkApi(token=token)
        self.api = self.vk_session.get_api()
        self.long_poll = VkBotLongPoll(vk=self.vk_session, group_id=group_id)

        self.scheduler = scheduler

    def run(self):
        """Запуск бота."""
        for event in self.long_poll.listen():
            try:
                self.handle_event(event)
            except Exception:
                log.exception('Ошибка в обработке события.')

    @db_session
    def handle_event(self, event):
        """
        Обработка полученного события.

        :param event: VkBotMessageEvent object
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info(f'Неизвестное событие - {event.type}')
            return

        user_id = str(event.object.message['peer_id'])
        text = event.object.message['text']

        user_state = UserState.get(user_id=user_id)
        user_subscribed = SubscribedUsers.get(user_id=user_id)

        if user_state:
            # Если пользователь внутри уже начатого сценария -> продолжение его выполнения
            text_to_send = self.continue_scenario(user_state, text, user_subscribed)
        else:
            # Если пользователь вне сценария -> определение намерения пользователя
            text_to_send, intent = self.define_intent(user_id, text, user_subscribed)
            if intent == 'unsubscribe':
                user_subscribed.delete()

        log.info('Отправляем пользователю сообщение.')
        random_id = randint(1, 2 ** 20)
        self.api.messages.send(user_id=user_id, random_id=random_id, message=text_to_send)

    def define_intent(self, user_id, text, user_subscribed):
        """
        Определение намерения пользователя.

        :param text: текст полученного сообщения
        :param user_subscribed: запись из БД c информацией по пользователю user_id
        """
        if user_subscribed:
            intents, default_answer = config.INTENTS_SUBSCRIBED, config.DEFAULT_ANSWER_SUBSCRIBED
        else:
            intents, default_answer = config.INTENTS_NON_SUBSCRIBED, config.DEFAULT_ANSWER_NON_SUBSCRIBED

        for intent in intents:
            if any(token in text.lower() for token in intent['tokens']):
                # Намерение определено через поиск в тексте соответствующего токена
                intent_name = intent["name"]
                log.debug(f'Для пользователя {user_id} определено намерение {intent_name}.')
                if not intent['scenario']:
                    # Если намерение не предполагает активации сценария -> отправка заготовленного сообщения
                    text_to_send = intent['answer']
                else:
                    text_to_send = self.start_scenario(user_id, intent['scenario'])
                break
        else:
            # Намерение не было определено через токен -> отправка дефолтного сообщения
            text_to_send, intent_name = default_answer, None
        return text_to_send, intent_name

    @db_session
    def start_scenario(self, user_id, scenario_name, meters=None):
        """Инициация выполнения сценария.

        :param dict meters: словарь, в который далее будут заноситься показания счетчиков
        :return: текст сообщения, которое будет отправлено пользователю; содержит объяснение того, что ему нужно
        сделать
        """

        scenario = config.SCENARIOS[scenario_name]
        first_step_name = scenario['first_step']
        step = scenario['steps'][first_step_name]
        text_to_send = step['text']
        if 'notify' in scenario_name:
            current_meter = meters[0]
            context = {'current_meter': current_meter, 'meters_data': {}, 'meters_ordered': meters}
        else:
            context = {}
        UserState(user_id=user_id, scenario_name=scenario_name, step_name=first_step_name, context=context)
        return text_to_send

    def continue_scenario(self, user_state, text, user_subscribed):
        """
        Продолжение выполнения сценария.

        :param user_state: запись из БД c информацией по состоянию пользователя в контексте продвижения по сценарию
        :param text: текст полученного сообщения
        :param user_subscribed: запись из БД c информацией по пользователю (имя, дата отправки показаний, адрес, email,
        типы счетчиков)
        :return: текст сообщения, которое будет отправлено пользователю; содержит объяснение того, что ему нужно
        сделать (если сценарий не завершен) либо подтверждение успешного внесения/изменения данных (если сценарий
        завершен)
        """
        steps = config.SCENARIOS[user_state.scenario_name]['steps']
        step = steps[user_state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text, user_state.context):
            # Данные введены по верному шаблону -> handler возвращает True -> переход на следующий шаг
            next_step_name = step['next_step']
            next_step = steps[next_step_name]
            text_to_send = next_step['text'].format(**user_state.context)

            # Проверка, является ли следующий шаг последним в сценарии
            if next_step['next_step']:
                # Не является -> фиксация нового шага сценария для данного пользователя
                user_state.step_name = next_step_name
            else:
                # Является -> завершение сценария
                self.finish_scenario(user_state, user_subscribed)
        else:
            # Данные введены не по шаблону -> handler возвращает False -> перехода на следующий шаг не происходит
            text_to_send = step['failure_text']

        return text_to_send

    def finish_scenario(self, user_state, user_subscribed):
        """
        Завершение выполнения сценария.

        :param user_state: запись из БД c информацией по состоянию пользователя в контексте продвижения по сценарию
        :param user_subscribed: запись из БД c информацией по пользователю (имя, дата отправки показаний, адрес, email,
        типы счетчиков)
        """
        user_id = user_state.user_id
        context = user_state.context
        scenario_name = user_state.scenario_name
        log.debug(f'Выполнение сценария для пользователя {user_id} завершено со следующими данными: '
                  f'{user_state.context}')
        if 'notify' in scenario_name:
            # Завершается сценарий notify -> отправить емейл, удалить из БД запись о состоянии пользователя в контексте
            # продвижения по сценарию и запланировать отправку пользователю уведомления vk в следующем месяце
            errors = send_email(context, user_subscribed)
            if 'notify_2_meters_or_more' in scenario_name:
                # Приведение сценария "notify_2_meters_or_more" к конфигурации по умолчанию
                config.SCENARIOS['notify_2_meters_or_more']['steps']['step_2']['next_step'] = 'step_2'
            if not errors:
                msg = f'Сообщение с показаниями на электронный адрес {user_subscribed.email} отправлено'
            else:
                msg = str(errors)
            log.info(msg)
            user_state.delete()
            self.scheduler.schedule_notification(bot, user_subscribed.date, user_id, user_subscribed.meters)
            return
        if 'edit' in scenario_name:
            # Редактирование уже занесенной в БД записи
            user_subscribed.set(**context)
        else:
            # Занесение записи с данными пользователя в БД и планирование отправки уведомления vk
            SubscribedUsers(user_id=user_id, **context)
            self.scheduler.schedule_notification(bot, context['date'], user_id, context['meters'])
        user_state.delete()

    @db_session
    def send_notification_message(self, user_id, meters):
        """
        Отправка пользователю сообщения на сайте vk.com, которое содержит:
        1. уведомление о наступлении дня подачи показаний счетчиков в управляющую компанию/управдому
        2. запрас самих показаний для последующей отправки

        :param dict meters: строка, в которой перечислены типы счетчиков, показания которых следует передать
        """
        meters_count = len(meters)
        scenario_name = 'notify_1_meter' if meters_count == 1 else 'notify_2_meters_or_more'
        text_to_send = bot.start_scenario(user_id, scenario_name, meters)
        user_state = UserState.get(user_id=user_id)
        text_to_send_formatted = text_to_send.format(**user_state.context)
        log.info('Отправляем пользователю уведомление о необходимости отправки показаний счетчиков.')
        random_id = randint(1, 2 ** 20)
        bot.api.messages.send(user_id=user_id, random_id=random_id, message=text_to_send_formatted)


if __name__ == '__main__':
    log = logging.getLogger('bot_log')
    configure_logging()
    scheduler = Scheduler()
    scheduler.start()
    bot = Bot(config.TOKEN, config.GROUP_ID, scheduler)
    scheduler.schedule_all_notifications(bot)
    bot.run()
