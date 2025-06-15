from aiogram.dispatcher.filters.state import StatesGroup, State


class TaklifState(StatesGroup):
    username = State()
    taklif = State()
