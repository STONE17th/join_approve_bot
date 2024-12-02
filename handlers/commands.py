from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.formatting import as_list, as_marked_section, Text
from psycopg2.errors import UniqueViolation

from datetime import datetime

from classes.classes import Admin, Channel, Request
from database.data_base import DataBase
from keyborads import inline_keyboards

from classes.scheduler import bot_scheduler

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
    date_created = datetime.now()
    try:
        Request.create(message.chat.id, message.from_user.id)
        # DataBase.add_request(message.chat.id, message.from_user.id, date_created)
    except UniqueViolation:
        pass


@commands_router.message(Command('str'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    min_count, max_count = map(int, message.text.split()[1:])
    list(admin.channels.values())[0].start_auto_approve((min_count, max_count))
    print('Запущен Таймер')


@commands_router.message(Command('stop'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    list(admin.channels.values())[0].stop_auto_approve()
    print('Таймер остановлен')


@commands_router.message(Command('lst'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    print(list(admin.channels.values())[0]._bot_scheduler.get_jobs())
    print(list(admin.channels.values())[0]._bot_scheduler.running)


@commands_router.message(Command('tst'))
async def test_scheduler(message: Message, bot: Bot, command: CommandObject):
    admin = Admin(84777589)
    print(admin.channels)
    channel = admin.channels[-1002131989863].requests
    sorted_channel = sorted(channel, key=lambda x: x.creation_date)
    count = 0
    for i in range(len(channel)):
        # print(channel[i])
        print(f'{str(channel[i]):>15} {str(sorted_channel[i]):<15}')
        if channel[i] == sorted_channel[i]:
            count += 1
    print(len(channel))
    print(count)


@commands_router.message(Command('refresh'))
async def refresh_channels(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    for channel_tg_id in admin.channels:
        channel = await bot.get_chat(channel_tg_id)
        DataBase.refresh_channels(channel.title, message.from_user.id, channel_tg_id)
