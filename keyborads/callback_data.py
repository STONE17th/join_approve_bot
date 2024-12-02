from aiogram.filters.callback_data import CallbackData


class CustomCallBack(CallbackData, prefix='RC'):
    target_handler: str
    value: str = 'None'
    requests: str = 'new'
    channel_tg_id: int = 0
    request_tg_id: int = 0
