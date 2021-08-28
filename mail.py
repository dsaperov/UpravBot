from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from config import EMAIL_FROM, EMAIl_PASSWORD


def send_email(context, user_data):
    """
    Отправка сообщения с полученными показаниями счетчиков на адрес электронной почти управляющей компании/управдома.

    :param context: словарь, содержащий фактические показания счетчиков, полученные от пользователя
    :param user_data: запись из БД c информацией по пользователю (имя, дата отправки показаний, номер квартиры, email,
    типы счетчиков)
    :return:
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'], msg['Subject'], body = get_email_data(context, user_data)

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com:587')
    # server.set_debuglevel(True)
    server.starttls()
    server.login(EMAIL_FROM, EMAIl_PASSWORD)
    server.send_message(msg)
    server.quit()


def get_email_data(context, user_data):
    """
    Формирование на основе полученных от пользователя данных:
    1. электронного адреса, на который необходимо отправить письмо
    2. темы письма с указанием фактического номера квартиры пользователя
    3. текста письма с указанием показаний счетчиков.

    :param context: словарь, содержащий фактические показания счетчиков, полученные от пользователя
    :param user_data: запись из БД c информацией по пользователю (имя, дата отправки показаний, номер квартиры, email,
    типы счетчиков)
    """
    email_to = user_data.email
    subject = f'Показания счётчиков, кв. {user_data.flat}'

    text = 'Добрый день! Прилагаю показания счетчиков.\n\n'
    meters_data = context['meters_data']
    for meter_name in context['meters_ordered']:
        text += f'{meter_name} - {meters_data[meter_name]}\n'
    text += '\n' \
            '---\n' \
            'С уважением,\n' \
            f'{user_data.name}'

    return email_to, subject, text
