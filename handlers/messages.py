from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from psycopg2.errors import UniqueViolation

from datetime import datetime

from classes.classes import Admin, Channel
from database.data_base import DataBase
from keyborads import inline_keyboards

from classes.scheduler import bot_scheduler

router = Router()


@router.message(Command('start'))
async def command_start(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    message_text = f'{message.from_user.full_name}, '
    channels_list = []
    if admin.channels:
        message_text += 'это твои каналы:\n'
        for channel in admin.channels.values():
            channel_title = await channel.title(bot)
            channels_list.append((channel_title, channel))
            message_text += f'{channel_title}: {len(channel.requests)} заявок\n'
    else:
        message_text += 'добавьте бота в канал для управления'
    await message.answer(
        text=message_text,
        reply_markup=inline_keyboards.kb_channels_list(channels_list)
    )


@router.message(F.forward_origin)
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


@router.chat_join_request()
async def new_request(message: Message, bot: Bot):
    date_created = datetime.now()
    try:
        DataBase().add_request(message.chat.id, message.from_user.id, date_created)
    except UniqueViolation:
        pass


@router.message(Command('str'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    min_count, max_count = map(int, message.text.split()[1:])
    list(admin.channels.values())[0].start_auto_approve((min_count, max_count))
    print('Запущен Таймер')


@router.message(Command('stop'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    list(admin.channels.values())[0].stop_auto_approve()
    print('Таймер остановлен')


@router.message(Command('lst'))
async def test_scheduler(message: Message, bot: Bot):
    admin = Admin(message.from_user.id)
    print(list(admin.channels.values())[0]._bot_scheduler.get_jobs())
    print(list(admin.channels.values())[0]._bot_scheduler.running)


@router.message(Command('tst'))
async def test_scheduler(message: Message, bot: Bot, command: CommandObject):
    print(command.args)
    print(command)
    print(command)
