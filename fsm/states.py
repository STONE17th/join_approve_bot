from aiogram.fsm.state import State, StatesGroup


class CallbackState(StatesGroup):
    channel_tg_id = State()
    group = State()
    amount = State()
    confirm = State()
