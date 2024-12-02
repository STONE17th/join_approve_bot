from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import as_list
from psycopg2.errors import UniqueViolation

from classes.classes import Admin, Request
from database.data_base import DataBase
from keyborads import inline_keyboards

commands_router = Router()


@commands_router.message(Command('start'))
async def command_start(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    message_rows = [f'{message.from_user.full_name}, приветствую тебя!']
    if admin.channels:
        message_rows.append('Выбери канал для управления')
    else:
        message_rows.append('Добавь бота в канал для управления')
    caption = as_list(
        *message_rows,
    )
    keyboard = inline_keyboards.kb_channels_list(admin)
    await message.answer(
        **caption.as_kwargs(),
        reply_markup=keyboard,
    )


@commands_router.message(F.forward_origin)
async def catch_forward_message(message: Message, bot: Bot):
    try:
        DataBase().add_channel(
            channel_tg_id=message.forward_origin.chat.id,
            admin_tg_id=message.from_user.id,
        )
        message_text = f'Канал {message.forward_origin.chat.title} успешно добавлен!'
    except UniqueViolation:
        message_text = 'Этот канал уже добавлен!'
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.send_message(message.chat.id, message_text)


@commands_router.chat_join_request()
async def new_request(message: Message, bot: Bot):
    try:
        Request.create(message.chat.id, message.from_user.id)
    except UniqueViolation:
        pass


@commands_router.message(Command('refresh'))
async def refresh_channels(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    for channel_tg_id in admin.channels:
        channel = await bot.get_chat(channel_tg_id)
        DataBase.refresh_channels(channel.title, message.from_user.id, channel_tg_id)
