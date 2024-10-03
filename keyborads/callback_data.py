from aiogram.filters.callback_data import CallbackData


class AdminChannel(CallbackData, prefix='AC'):
    button: str
    admin_tg_id: int
    channel_tg_id: int


class NewOrOld(CallbackData, prefix='NO'):
    button: str = 'new_old'
    value: str
