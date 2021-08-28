from pony.orm import Database, Required, Json

from config import DATABASE_CONFIG

database = Database()
database.bind(**DATABASE_CONFIG)


class UserState(database.Entity):
    """Состояние пользователя внутри сценария"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class SubscribedUsers(database.Entity):
    """Данные пользователей сервиса"""
    user_id = Required(str, unique=True)
    date = Required(int)
    email = Required(str)
    flat = Required(int)
    name = Required(str)
    meters = Required(str)


database.generate_mapping(create_tables=True)
