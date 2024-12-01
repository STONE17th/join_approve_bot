from aiogram.filters.callback_data import CallbackData


# class NewOrOld(CallbackData, prefix='NOO'):
#     button: str = 'select_option'
#     value: str = 'None'


class CustomCallBack(CallbackData, prefix='RC'):
    target_handler: str
    value: str = 'None'
    requests: str = 'new'
    channel_tg_id: int = 0
    request_tg_id: int = 0


# class RequestsGroup(CallbackData, prefix='RG'):
#     button: str = 'requests_group'
#     value: str


# class ConfirmCallback(CallbackData, prefix='CC'):
#     button: str = 'confirm_join'
#     value: str


# class BackButton(CallbackData, prefix='BB'):
#     button: str = 'back_button'
#     menu: str
