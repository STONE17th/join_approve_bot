from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import CustomCallBack
from classes import Admin, Channel


async def kb_channels_list(admin: Admin, bot: Bot):
    keyboard = InlineKeyboardBuilder()
    for channel in admin.channels.values():
        channel_title = await channel.title(bot)
        channel_requests = channel.requests
        keyboard.button(
            text=f'{channel_title}: {len(channel_requests)}',
            callback_data=CustomCallBack(
                target_handler='select_channel',
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


def kb_select_option(channel: Channel):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Старые',
        callback_data=CustomCallBack(
            target_handler='select_option',
            requests='old',
        ),
    )
    keyboard.button(
        text=('OFF' if channel.check_auto else 'ON'),
        callback_data=CustomCallBack(
            target_handler='select_option',
            requests='auto',
        ),
    )
    keyboard.button(
        text='Новые',
        callback_data=CustomCallBack(
            target_handler='select_option',
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


def kb_confirm(channel_tg_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Да',
        callback_data=CustomCallBack(
            target_handler='confirm_approve',
            channel_tg_id=channel_tg_id,
        ),
    )
    keyboard.button(
        text='Назад',
        callback_data=CustomCallBack(
            target_handler='select_channel',
            channel_tg_id=channel_tg_id,
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


def back_button(channel_tg_id: int, target: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Назад',
        callback_data=CustomCallBack(
            target_handler=target,
            channel_tg_id=channel_tg_id,
        ),
    )
    return keyboard.as_markup()
