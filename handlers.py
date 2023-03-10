"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True, если шаг пройден, и False, если данные введены неправильно.
"""

import re

from config import SCENARIOS, EMAIL_SUBJECT_TEXT


def handle_date(text, user_state):
    """Обработка сообщения пользователя с датой отправки показаний.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранятся данные,
    предоставляемые пользователем в ходе продвижения по сценарию. Для добавления новых данных используется метод
    update_context(). После завершения сценария данные из user_state.context_json будут перенесены в таблицу
    subscribedusers.
    """
    date_pattern = r'^([а-яА-Я]*\s)*([1-9]|[12][0-9]|3[01])$'

    match = re.match(date_pattern, text)
    if match:
        user_state.update_context('date', int(match[2]))
        return True
    else:
        return False


def handle_email(text, user_state):
    """Обработка сообщения пользователя с адресом электронной почты.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранятся данные,
    предоставляемые пользователем в ходе продвижения по сценарию. Для добавления новых данных используется метод
    update_context(). После завершения сценария данные из user_state.context_json будут перенесены в таблицу
    subscribedusers.
    """
    email_pattern = r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b'

    match = re.search(email_pattern, text)
    if match:
        user_state.update_context('email', match.group())
        return True
    else:
        return False


def handle_address(text, user_state):
    """Обработка сообщения пользователя с адресом.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранятся данные,
    предоставляемые пользователем в ходе продвижения по сценарию. Для добавления новых данных используется метод
    update_context(). После завершения сценария данные из user_state.context_json будут перенесены в таблицу
    subscribedusers.
    """
    max_address_length = 255 - len(EMAIL_SUBJECT_TEXT + ', ')
    address_pattern = fr'^(?=[А-я])(?=.*?\d).{{2,{max_address_length}}}$'

    match = re.search(address_pattern, text)
    if match:
        user_state.update_context('address', text)
        return True
    else:
        return False


def handle_name(text, user_state):
    """Обработка сообщения пользователя с его именем.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранятся данные,
    предоставляемые пользователем в ходе продвижения по сценарию. Для добавления новых данных используется метод
    update_context(). После завершения сценария данные из user_state.context_json будут перенесены в таблицу
    subscribedusers.
    """
    name_pattern = r'^\w+$'

    match = re.search(name_pattern, text)
    if match:
        user_state.update_context('name', text.capitalize())
        return True
    else:
        return False


def handle_meters(text, user_state):
    """Обработка сообщения пользователя с перечислением типов счетчиков, данные по которым следует передавать.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранятся данные,
    предоставляемые пользователем в ходе продвижения по сценарию. Для добавления новых данных используется метод
    update_context(). После завершения сценария данные из user_state.context_json будут перенесены в таблицу
    subscribedusers.
    """
    meters_pattern = r'[а-яА-Я][а-яА-Я.\s]+[а-яА-Я]'

    findings_list = re.findall(meters_pattern, text)
    if findings_list:
        findings_set = set(findings_list)
        contains_duplicates = len(findings_list) != len(findings_set)
        if contains_duplicates:
            return False
        user_state.update_context('meters', ', '.join(findings_list))
        return True
    else:
        return False


def handle_meters_data(text, user_state):
    """Обработка сообщения пользователя с указанными показаниями по какому-либо счетчику.

    :param str text: текст сообщения пользователя
    :param UserState user_state: экземпляр модели UserState, содержащий информацию о состоянии пользователя в контексте
    продвижения по сценарию. Имеет атрибут context_json, представляющий собой JSON-строку, в которой хранится
    информация о типах счетчиков, данные по которым необходимо отправить, а также сами показания счетчиков,
    которые пользователь предоставляет в ходе продвижения по сценарию notify. Для получения данных, хранящихся в
    user_state.context_json, используется обращение к свойству user_state.context.
    """
    meters_data_pattern = r'^\d+(\.\d+)*$'

    match = re.match(meters_data_pattern, text)
    if match:
        current_meter = user_state.context['current_meter']
        user_state.update_context('meters_data', current_meter, text)
        meters = user_state.context['meters_ordered']
        meters_count = len(meters)
        if meters_count == 1:
            return True

        current_meter_index = meters.index(current_meter)
        if current_meter_index < meters_count - 1:
            # Текущий счетчик НЕ последний -> назначить следующий счетчик в качестве текущего
            user_state.update_context('current_meter', meters[current_meter_index + 1])
        else:
            # Текущий счетчик последний -> переход с текущего шага на финальный Шаг 3 -> отправка письма со всеми
            # полученными показаниями счетчиков
            SCENARIOS['notify_2_meters_or_more']['steps']['step_2']['next_step'] = 'step_3'
        return True
    else:
        return False
