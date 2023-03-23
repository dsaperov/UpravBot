import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pony.orm import db_session, select

from models import SubscribedUsers

log = logging.getLogger('bot_log')


class Scheduler(BackgroundScheduler):
    """Планировщик задач."""

    def schedule_all_notifications(self, bot):
        """
        Планирование отправки уведомлений всем пользователям, данные о которых присутствуют в БД. Выполняется при каждом
        запуске приложения, благодаря чему при перезагрузке сервера и вынужденном перезапуске программы все слетевшие
        уведомления будут запланированы заново.
        """

        all_users = select(user for user in SubscribedUsers)

        with db_session:
            for user in all_users:
                self.schedule_notification(bot, user.date, user.user_id, user.meters)

    def schedule_notification(self, bot, notification_day, user_id, meters):
        """
        Непосредственное внесение задачи по отправке уведомления в планировщик.

        :param bot: объект бота
        :param int notification_day: день, указанный пользователем в качестве дня отправки показаний счетчиков
        :param str meters: строка, в которой перечислены типы счетчиков, показания по которым следует передать
        """
        meters_list = meters.split(', ')
        cron_trigger = CronTrigger(day=notification_day, hour=23, minute=42)
        job = self.add_job(bot.send_notification_message, id=user_id, trigger=cron_trigger, args=[user_id, meters_list])
        log.debug(f'В планировщик добавлена новая задача: {job}')

