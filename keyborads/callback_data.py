from aiogram.filters.callback_data import CallbackData


class ApproveUsers(CallbackData, prefix='AU'):
    menu: str
    button: str = ''
    value: str = ''
    admin_tg_id: int = 0
    channel_tg_id: int = 0
    user_tg_id: int = 0


# class AdminChannel(CallbackData, prefix='AC'):
#     button: str
#     admin_tg_id: int
#     channel_tg_id: int


class NewOrOld(CallbackData, prefix='NO'):
    button: str = 'new_old'
    value: str


class ConfirmCallback(CallbackData, prefix='CC'):
    button: str = 'confirm_join'
    value: str


class BackButton(CallbackData, prefix='BB'):
    button: str = 'back_button'
    menu: str
