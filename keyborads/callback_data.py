from aiogram.filters.callback_data import CallbackData


class TestButton(CallbackData, prefix='TEST'):
    button: str


class RequestChannel(CallbackData, prefix='RC'):
    target: str
    value: str = 'None'
    admin_tg_id: int = 0
    channel_tg_id: int = 0
    user_tg_id: int = 0


class NewOrOld(CallbackData, prefix='NO'):
    button: str = 'new_old'
    value: str


class ConfirmCallback(CallbackData, prefix='CC'):
    button: str = 'confirm_join'
    value: str


class BackButton(CallbackData, prefix='BB'):
    button: str = 'back_button'
    menu: str
