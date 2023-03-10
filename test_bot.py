from copy import deepcopy
from random import randint
from unittest import TestCase, main
from unittest.mock import Mock, patch

from pony.orm import db_session
from vk_api.bot_longpoll import VkBotMessageEvent

import bot
from models import SubscribedUsers, UserState

import config

USERNAME = 'Александр'
COLD_WATER_METER = 'холодная вода'
HOT_WATER_METER = 'горячая вода'
HEAT_METER = 'отопление'
ADDRESS = 'кв. 1'


@patch('bot.log', new=Mock(), create=True)
class RunTest(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {
            'message': {
                'date': 1627210187,
                'from_id': 0,
                'id': 466,
                'out': 0,
                'peer_id': 0,
                'text': 'привет',
                'conversation_message_id': 462,
                'fwd_messages': [],
                'important': False,
                'random_id': 0,
                'attachments': [],
                'is_hidden': False
            },
            'client_info': {
                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback', 'intent_subscribe',
                                   'intent_unsubscribe'],
                'keyboard': True,
                'inline_keyboard': True,
                'carousel': True,
                'lang_id': 0
            }
        },
        'group_id': 204386139,
        'event_id': '61ae537413097a243e06438453d807707e53b185'
    }

    INPUTS = [
        'Привет',
        'Что ты можешь?',
        'Начать',
        '32',
        '21',
        'upravdom@my_house.com',
        'upravdom@myhouse.com',
        '.' * 256,
        ADDRESS,
        'Jones.01',
        USERNAME,
        'cold, hot, electricity',
        f'{COLD_WATER_METER}, {HOT_WATER_METER}, {HEAT_METER}'
    ]

    EXPECTED_OUTPUTS = [
        config.DEFAULT_ANSWER_NON_SUBSCRIBED,
        config.INTENTS_NON_SUBSCRIBED[0]['answer'],
        config.SCENARIOS['set_configs']['steps']['step_1']['text'],
        config.SCENARIOS['set_configs']['steps']['step_1']['failure_text'],
        config.SCENARIOS['set_configs']['steps']['step_2']['text'],
        config.SCENARIOS['set_configs']['steps']['step_2']['failure_text'],
        config.SCENARIOS['set_configs']['steps']['step_3']['text'],
        config.SCENARIOS['set_configs']['steps']['step_3']['failure_text'],
        config.SCENARIOS['set_configs']['steps']['step_4']['text'],
        config.SCENARIOS['set_configs']['steps']['step_4']['failure_text'],
        config.SCENARIOS['set_configs']['steps']['step_5']['text'],
        config.SCENARIOS['set_configs']['steps']['step_5']['failure_text'],
        config.SCENARIOS['set_configs']['steps']['step_6']['text'].format(date=INPUTS[4])
    ]

    def test_run(self):
        events_number = randint(10, 50)
        events_content = randint(1, 9)
        events_list = [events_content for _ in range(events_number)]

        bot.vk_api.VkApi = Mock()
        long_poll_mock = Mock()
        long_poll_mock.listen = Mock(return_value=events_list)
        bot.VkBotLongPoll = Mock(return_value=long_poll_mock)
        scheduler = Mock()

        test_bot = bot.Bot('', '', scheduler)
        test_bot.handle_event = Mock()
        test_bot.run()

        test_bot.handle_event.assert_called()
        test_bot.handle_event.assert_called_with(events_content)
        assert test_bot.handle_event.call_count == events_number

    def test_handle_event(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poll_mock = Mock()
        long_poll_mock.listen = Mock(return_value=events)
        scheduler = Mock()

        with patch('bot.VkBotLongPoll', return_value=long_poll_mock):
            with patch('scheduler.Scheduler.schedule_notification', return_value=None):
                with patch('bot.bot',  create=True, return_value=Mock):
                    test_bot = bot.Bot('', '', scheduler)
                    test_bot.api = api_mock
                    test_bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call_args in send_mock.call_args_list:
            kwargs = call_args[1]
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    @classmethod
    @db_session
    def tearDownClass(cls):
        test_id = str(RunTest.RAW_EVENT['object']['message']['from_id'])

        for table in (SubscribedUsers, UserState):
            test_record = table.get(user_id=test_id)
            test_record.delete() if test_record else None


if __name__ == '__main__':
    main()
