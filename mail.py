import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from config import EMAIL_FROM, EMAIl_PASSWORD, EMAIL_HOST, EMAIL_PORT


def send_email(context, user_data):
    """
    Отправка сообщения с полученными показаниями счетчиков на адрес электронной почти управляющей компании/управдома.

    :param context: словарь, содержащий фактические показания счетчиков, полученные от пользователя
    :param user_data: запись из БД c информацией по пользователю (имя, дата отправки показаний, адрес, email,
    типы счетчиков)
    :return:
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'], msg['Subject'], body = get_email_data(context, user_data)
    msg.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, context=context) as server:
        # server.starttls(context=context)
        # server.set_debuglevel()
        server.login(EMAIL_FROM, EMAIl_PASSWORD)
        recipients = [msg['To'], EMAIL_FROM]
        errors = server.send_message(msg=msg, to_addrs=recipients)

    return errors


def get_email_data(context, user_data):
    """
    Формирование на основе полученных от пользователя данных:
    1. электронного адреса, на который необходимо отправить письмо
    2. темы письма с указанием адреса пользователя
    3. текста письма с указанием показаний счетчиков.

    :param context: словарь, содержащий фактические показания счетчиков, полученные от пользователя
    :param user_data: запись из БД c информацией по пользователю (имя, дата отправки показаний, адрес, email,
    типы счетчиков)
    """
    email_to = user_data.email
    subject = f'Показания счётчиков ({user_data.address})'

    body = 'Добрый день! Прилагаю показания счетчиков.\n\n'
    meters_data = context['meters_data']
    for meter_name in context['meters_ordered']:
        body += f'{meter_name.capitalize()} — {meters_data[meter_name]}\n'
    body += '\n' \
            '---\n' \
            'С уважением,\n' \
            f'{user_data.name}'

    return email_to, subject, body
