from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import CustomCallBack
from classes import Admin, Channel


def kb_channels_list(admin: Admin):
    keyboard = InlineKeyboardBuilder()
    for channel in admin.channels.values():
        keyboard.button(
            text=f'{channel.title}',
            callback_data=CustomCallBack(
                target_handler='control_channel',
                channel_tg_id=channel.channel_tg_id,
            ),
        )
    keyboard.button(
        text='Помощь',
        callback_data=CustomCallBack(
            target_handler='help',
        ),
    )
    # keyboard.adjust(*[1] * len(admin.channels), 1)
    keyboard.adjust(1)
    return keyboard.as_markup()


def kb_select_approve_type(channel: Channel):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Старые',
        callback_data=CustomCallBack(
            target_handler='type_selected',
            requests='old',
        ),
    )
    keyboard.button(
        text=('OFF' if channel.check_auto else 'ON'),
        callback_data=CustomCallBack(
            target_handler='auto_approve_stop' if channel.check_auto else 'type_selected',
            requests='auto',
        ),
    )
    keyboard.button(
        text='Новые',
        callback_data=CustomCallBack(
            target_handler='type_selected',
            requests='new',
        ),
    )
    keyboard.button(
        text='Назад',
        callback_data=CustomCallBack(
            target_handler='main_menu',
        ),
    )
    keyboard.adjust(3, 1)
    return keyboard.as_markup()


def kb_confirm():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Да',
        callback_data=CustomCallBack(
            target_handler='confirm_approve',
        ),
    )
    keyboard.button(
        text='Назад',
        callback_data=CustomCallBack(
            target_handler='back',
        ),
    )
    keyboard.button(
        text='Главное меню',
        callback_data=CustomCallBack(
            target_handler='main_menu',
        ),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def back_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Назад',
        callback_data=CustomCallBack(
            target_handler='back',
            # channel_tg_id=channel_tg_id,
        ),
    )
    return keyboard.as_markup()
