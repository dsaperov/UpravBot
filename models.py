import json
from collections import defaultdict

from pony.orm import Database, Required, LongStr

from config import DATABASE_CONFIG

database = Database()
database.bind(**DATABASE_CONFIG)


class UserState(database.Entity):
    """Состояние пользователя внутри сценария"""
    CONTEXT_COLUMN_NAME = 'context'

    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context_json = Required(LongStr, column=CONTEXT_COLUMN_NAME)

    def __init__(self, **kwargs):
        self._process_kwargs(kwargs)
        super().__init__(**kwargs)

    def set(self, **kwargs):
        self._process_kwargs(kwargs)
        super().set(**kwargs)

    def _process_kwargs(self, kwargs):
        if self.CONTEXT_COLUMN_NAME in kwargs:
            kwargs['context_json'] = json.dumps(kwargs.pop(self.CONTEXT_COLUMN_NAME))

    @property
    def context(self):
        return json.loads(self.context_json)

    @context.setter
    def context(self, value):
        self.context_json = json.dumps(value)

    def update_context(self, *args):
        context = defaultdict(dict, self.context)
        keys = list(args[:-1])
        value = args[-1]
        if len(keys) == 1:
            context[keys[0]] = value
        else:
            top_key = keys.pop(0)
            context[top_key].update(self._get_nested_context(keys, value))
        self.context = context

    def _get_nested_context(self, keys, value):
        key = keys.pop(0)
        if not keys:
            return {key: value}
        else:
            return {key: self._get_nested_context(keys, value)}


class SubscribedUsers(database.Entity):
    """Данные пользователей сервиса"""
    user_id = Required(str, unique=True)
    date = Required(int)
    email = Required(str)
    address = Required(str)
    name = Required(str)
    meters = Required(str)


database.generate_mapping(create_tables=True)
