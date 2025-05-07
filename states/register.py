from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_for_language = State()
    waiting_for_phone = State()
    waiting_for_code = State()
