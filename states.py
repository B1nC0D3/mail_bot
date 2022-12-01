from aiogram.dispatcher.filters.state import State, StatesGroup


class Settings(StatesGroup):
    waiting_for_mail_login = State()
    waiting_for_mail_password = State()
    waiting_for_mail_domen = State()
    settings_done = State()
