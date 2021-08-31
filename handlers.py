"""
Handler - функция, которая принимает на вход text (текст входящего сообщения) и context (dict), а возвращает bool:
True, если шаг пройден, и False, если данные введены неправильно.
"""

import re

from config import SCENARIOS


def handle_date(text, context):
    """Обработка сообщения пользователя с датой отправки показаний.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию, предоставляемую пользователем в ходе продвижения
    по сценарию. После заверешения сценария данные из context будут перенесены в таблицу subscribedusers.
    """
    date_pattern = r'^([а-яА-Я]*\s)*([1-9]|[12][0-9]|3[01])$'

    match = re.match(date_pattern, text)
    if match:
        context['date'] = int(match[2])
        return True
    else:
        return False


def handle_email(text, context):
    """Обработка сообщения пользователя с адресом электронной почты.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию, предоставляемую пользователем в ходе продвижения
    по сценарию. После заверешения сценария данные из context будут перенесены в таблицу subscribedusers.
    """
    email_pattern = r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b'

    match = re.search(email_pattern, text)
    if match:
        context['email'] = match.group()
        return True
    else:
        return False


def handle_flat(text, context):
    """Обработка сообщения пользователя с номером квартиры.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию, предоставляемую пользователем в ходе продвижения
    по сценарию. После заверешения сценария данные из context будут перенесены в таблицу subscribedusers.
    """
    flat_pattern = r'^[0-9]+$'

    match = re.search(flat_pattern, text)
    if match:
        context['flat'] = text
        return True
    else:
        return False


def handle_name(text, context):
    """Обработка сообщения пользователя с его именем.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию, предоставляемую пользователем в ходе продвижения
    по сценарию. После заверешения сценария данные из context будут перенесены в таблицу subscribedusers.
    """
    flat_pattern = r'^\w+$'

    match = re.search(flat_pattern, text)
    if match:
        context['name'] = text.capitalize()
        return True
    else:
        return False


def handle_meters(text, context):
    """Обработка сообщения пользователя с перечислением типов счетчиков, данные по которым следует передавать.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию, предоставляемую пользователем в ходе продвижения
    по сценарию. После заверешения сценария данные из context будут перенесены в таблицу subscribedusers.
    """
    meters_pattern = r'[а-яА-Я][а-яА-Я.\s]+[а-яА-Я]'

    findings_list = re.findall(meters_pattern, text)
    if findings_list:
        findings_set = set(findings_list)
        contains_duplicates = len(findings_list) != len(findings_set)
        if contains_duplicates:
            return False
        context['meters'] = ', '.join(findings_list)
        return True
    else:
        return False


def handle_meters_data(text, context):
    """Обработка сообщения пользователя с указанными показаниями по какому-либо счетчику.

    :param str text: текст сообщения пользователя
    :param pony.orm.ormtypes.TrackedDict context: содержит информацию о типах счетчиков, данные по которым необходимо 
    отправить, а также сами показания счетчиков, которые пользователь предоставляет в ходе продвижения по сценарию 
    notify
    """
    meters_data_pattern = r'^\d+(\.\d+)*$'

    match = re.match(meters_data_pattern, text)
    if match:
        current_meter = context['current_meter']
        context['meters_data'][current_meter] = text
        meters = context['meters_ordered']
        meters_count = len(meters)
        if meters_count == 1:
            return True

        current_meter_index = meters.index(current_meter)
        if current_meter_index < meters_count - 1:
            # Текущий счетчик НЕ последний -> назначить следующий счетчик в качестве текущего
            context['current_meter'] = meters[current_meter_index + 1]
        else:
            # Текущий счетчик последний -> переход с текущего шага на финальный Шаг 3 -> отправка письма со всеми
            # полученными показаниями счетчиков
            SCENARIOS['notify_2_meters_or_more']['steps']['step_2']['next_step'] = 'step_3'
        return True
    else:
        return False
