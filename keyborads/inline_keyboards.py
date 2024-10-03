from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from .callback_data import AdminChannel, NewOrOld


def kb_channels_admin(admin_tg_id, channels: list):
    keyboard = InlineKeyboardBuilder()
    for channel_title, channel_tg_id in channels:
        keyboard.button(text=channel_title, callback_data=AdminChannel(
            button='start',
            admin_tg_id=admin_tg_id,
            channel_tg_id=channel_tg_id))
    return keyboard.as_markup()


def kb_new_or_old():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Старые', callback_data=NewOrOld(value='old'))
    keyboard.button(text='Новые', callback_data=NewOrOld(value='new'))
    keyboard.button(text='Назад', callback_data=NewOrOld(value='main_menu'))
    keyboard.adjust(2, 1)
    return keyboard.as_markup()
