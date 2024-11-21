from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import NewOrOld, ConfirmCallback, RequestChannel
from classes import Channel


def kb_channels_list(channels_list: list[tuple[str, Channel]]):
    keyboard = InlineKeyboardBuilder()
    for title, channel in channels_list:
        keyboard.button(
            text=title,
            callback_data=RequestChannel(
                target='select_channel',
                admin_tg_id=channel.admin_tg_id,
                channel_tg_id=channel.channel_tg_id,
            ),
        )
    keyboard.button(
        text='Помощь',
        callback_data=RequestChannel(target='help'))
    keyboard.adjust(*[1] * len(channels_list), 1)
    return keyboard.as_markup()


def kb_new_or_old(channel: Channel):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Старые', callback_data=NewOrOld(value='old'))
    keyboard.button(
        text=('OFF' if channel.check_auto else 'ON'),
        callback_data=NewOrOld(value='random'))
    keyboard.button(text='Новые', callback_data=NewOrOld(value='new'))
    keyboard.button(text='Назад', callback_data=RequestChannel(target='main_menu'))
    keyboard.adjust(3, 1)
    return keyboard.as_markup()


def kb_confirm(channel_tg_id: int, admin_tg_id: int):
    keyboard = InlineKeyboardBuilder()
    print(channel_tg_id)
    keyboard.button(text='Да', callback_data=ConfirmCallback(value='yes'))
    keyboard.button(text='Назад', callback_data=RequestChannel(
        target='select_channel',
        admin_tg_id=admin_tg_id,
        channel_tg_id=channel_tg_id,
    ),
                    )
    keyboard.button(text='Главное меню', callback_data=RequestChannel(target='main_menu'))
    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def back_button(admin_tg_id: int, channel_tg_id: int, target: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад', callback_data=RequestChannel(
        target=target,
        admin_tg_id=admin_tg_id,
        channel_tg_id=channel_tg_id,
    ))
    return keyboard.as_markup()
