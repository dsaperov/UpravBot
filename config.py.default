import os

TOKEN = os.getenv('TOKEN')
GROUP_ID = 204386139

EMAIL_SUBJECT_TEXT = 'Показания счетчиков'
EMAIL_FROM = 'upravbot.service@inbox.ru'
EMAIl_PASSWORD = os.getenv('EMAIL_PASSWORD')


INTENTS_NON_SUBSCRIBED = [
    {
        'name': 'functionality',
        'tokens': ('можешь', 'умеешь', 'помощь'),
        'scenario': None,
        'answer': 'Я умею отправлять показатели счетчиков в управляющую компанию или управдому. Для этого '
                  'нужно сначала установить параметры отправки. Чтобы начать, отправьте сообщение "Начать".'
    },
    {
        'name': 'set_configs',
        'tokens': ('начать',),
        'scenario': 'set_configs',
        'answer': None
    },
]

INTENTS_SUBSCRIBED = [
    {
        'name': 'edit_date',
        'tokens': ('изменить дату',),
        'scenario': 'edit_date',
        'answer': None
    },
    {
        'name': 'edit_email',
        'tokens': ('изменить почту',),
        'scenario': 'edit_email',
        'answer': None
    },
    {
        'name': 'edit_address',
        'tokens': ('изменить адрес', 'изменить номер', 'изменить квартиру'),
        'scenario': 'edit_address',
        'answer': None
    },
    {
        'name': 'edit_meters',
        'tokens': ('изменить типы счетчиков',),
        'scenario': 'edit_meters',
        'answer': None
    },
    {
        'name': 'unsubscribe',
        'tokens': ('больше не пиши',),
        'scenario': None,
        'answer': 'Отлично, я больше не буду запрашивать у вас показания счетчиков.'
    },
]

SCENARIOS = {
    'set_configs': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Введите дату ежемесячной отправки показаний счетчиков. Каждый месяц в этот день я буду у вас'
                        ' их запрашивать. Например: 21',
                'failure_text': 'Дата должна быть числом в диапазоне от 1 до 31. Попробуйте еще раз.',
                'handler': 'handle_date',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Теперь введите email, на который нужно отравлять показания.',
                'failure_text': 'Во введенном адресе ошибка. Попробуйте еще раз.',
                'handler': 'handle_email',
                'next_step': 'step_3'
            },
            'step_3': {
                'text': 'Теперь введите свой адрес:\n'
                        '- номер квартиры, если показания будут отправляться в ТСЖ/управдому. Например: "кв. 1".\n'
                        '- полный адрес, если получатель - управляющая компания. Например: "Звездный бульвар, д. 1, '
                        'кв. 1" \n\n'
                        'Эти данные будут указаны в теме отправляемого письма.',
                'failure_text': f'Адрес должен начинаться с буквы русского алфавита, содержать хотя бы одну цифру и '
                                f'иметь длину от 2 до {255 - (len(EMAIL_SUBJECT_TEXT + ", "))} символов. Попробуйте '
                                f'еще раз.',
                'handler': 'handle_address',
                'next_step': 'step_4'
            },
            'step_4': {
                'text': 'Теперь введите Ваше имя. Оно будет указано в подписи письма.',
                'failure_text': 'Какое-то странное имя. Попробуйте еще раз.',
                'handler': 'handle_name',
                'next_step': 'step_5'
            },
            'step_5': {
                'text': 'Теперь перечислите через запятую типы счетчиков, показания которых нужно будет отправлять. '
                        'Например: холодная вода, гор. вода, отопление',
                'failure_text': 'Сообщение может состоять из букв русского алфавита, точек, пробелов и запятых. '
                                'Попробуйте еще раз.',
                'handler': 'handle_meters',
                'next_step': 'step_6'
            },
            'step_6': {
                'text': 'Отлично, теперь {date} числа каждого месяца я буду запрашивать у вас показания '
                        'счетчиков.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'edit_date': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Введите новую дату ежемесячной отправки показаний счетчиков. Например: 21',
                'failure_text': 'Дата должна быть числом в диапазоне от 1 до 31. Попробуйте еще раз.',
                'handler': 'handle_date',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Отлично, теперь {date} числа каждого месяца я буду запрашивать у вас показания '
                        'счетчиков.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'edit_address': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Введите новый адрес',
                'failure_text': f'Адрес должен начинаться с буквы русского алфавита, содержать хотя бы одну цифру и '
                                f'иметь длину от 2 до {255 - (len(EMAIL_SUBJECT_TEXT + ", "))} символов. Попробуйте '
                                f'еще раз.',
                'handler': 'handle_address',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Отлично, адрес изменен изменен на {address}.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'edit_email': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Введите новый email, на который нужно отравлять показания.',
                'failure_text': 'Во введенном адресе ошибка. Попробуйте еще раз.',
                'handler': 'handle_email',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Отлично, теперь я буду отправлять показания на {email}',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'edit_meters': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Перечислите через запятую типы счетчиков, показания которых нужно будет отправлять. '
                        'Например: холодная вода, гор. вода, отопление',
                'failure_text': 'Сообщение может состоять из букв русского алфавита, точек, пробелов и запятых. '
                                'Попробуйте еще раз.',
                'handler': 'handle_meters',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Отлично, теперь я буду отправлять показания следующих счетчиков: {meters}',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'notify_1_meter': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Добрый день! Сегодня - день отправки данных счетчиков. Отправьте мне показания счетчика '
                        '"{current_meter}". В качестве десятичного разделителя используйте точку. Например: 100.0.',
                'failure_text': 'Использован неверный формат. Попробуйте еще раз.',
                'handler': 'handle_meters_data',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Данные приняты. Письмо на указанный адрес электронной почты отправлено.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    },
    'notify_2_meters_or_more': {
        'first_step': 'step_1',
        'steps': {
            'step_1': {
                'text': 'Добрый день! Сегодня - день отправки данных счетчиков. Отправьте мне показания счетчика '
                        '"{current_meter}". В качестве десятичного разделителя используйте точку. Например: 100.0.',
                'failure_text': 'Использован неверный формат. Попробуйте еще раз.',
                'handler': 'handle_meters_data',
                'next_step': 'step_2'
            },
            'step_2': {
                'text': 'Теперь отправьте мне показания счетчика {current_meter}',
                'failure_text': 'Использован неверный формат. Попробуйте еще раз.',
                'handler': 'handle_meters_data',
                'next_step': 'step_2'
            },
            'step_3': {
                'text': 'Данные приняты. Письмо на указанный адрес электронной почты отправлено.',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }
    }
}

DEFAULT_ANSWER_NON_SUBSCRIBED = 'Для того, чтобы начать использование, просто спросите меня о том, что я могу или ' \
                                'введите "Помощь".'

DEFAULT_ANSWER_SUBSCRIBED = 'Если хотите изменить параметры отправки показаний, то укажите в сообщении, что именно ' \
                            'нужно поменять. Например:\n' \
                            '- изменить дату\n' \
                            '- изменить почту\n' \
                            '- изменить адрес\n' \
                            '- изменить типы счетчиков \n\n' \
                            'Если больше не хотите польоваться сервисом, отправьте "Больше не пиши мне".'

DATABASE_CONFIG = {
    'provider': 'postgres',
    'user': os.getenv('DATABASE_USERNAME'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'database': os.getenv('DATABASE_NAME')
}
