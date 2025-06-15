from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_for_shop_code = State()
    waiting_for_language = State()
    waiting_for_phone = State()


class PaymentStates(StatesGroup):
    waiting_for_chek = State()