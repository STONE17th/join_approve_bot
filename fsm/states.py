from aiogram.fsm.state import State, StatesGroup


class CallbackState(StatesGroup):
    target_channel = State()
    requests_type = State()
    requests_amount = State()
    confirm_approve = State()
    cancel_auto_approve = State()
