from aiogram.filters.callback_data import CallbackData


class NewOrOld(CallbackData, prefix='NOO'):
    button: str = 'select_option'
    value: str = 'None'


class RequestChannel(CallbackData, prefix='RC'):
    target: str
    value: str = 'None'
    admin_tg_id: int = 0
    channel_tg_id: int = 0
    user_tg_id: int = 0


class RequestsGroup(CallbackData, prefix='RG'):
    button: str = 'requests_group'
    value: str


class ConfirmCallback(CallbackData, prefix='CC'):
    button: str = 'confirm_join'
    value: str


class BackButton(CallbackData, prefix='BB'):
    button: str = 'back_button'
    menu: str
