import os
import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

from database.data_base import DataBase
from keyborads import inline_keyboards
from fsm import router as fsm_router

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

router = Router()

dp.include_routers(router, fsm_router)
db = DataBase()


@router.message(Command('start'))
async def com_add(message: Message, bot: Bot):
    channels = []
    for channel_tg_id in db.load_admin_channels(message.from_user.id):
        channel = await bot.get_chat(channel_tg_id)
        channels.append((channel.title, channel_tg_id))
    await message.answer('Выберите канал для управления:',
                         reply_markup=inline_keyboards.kb_channels_admin(message.from_user.id, channels))


@router.chat_join_request()
async def incoming_join_request(message: Message, bot: Bot):
    db.add_join_request(message.chat.id, message.from_user.id)
    await bot.send_message(409205647, str(message.from_user.id))
    # await bot.send_message(409205647, str(message.chat.id))


@router.message(F.text.startswith('approve'))
async def approve_incoming_user(message: Message, bot: Bot):
    msg = message.text.split()
    if len(msg) == 2 and msg[1].isdigit() and (msg[0].endswith('old') or msg[0].endswith('new')):
        users_count = int(message.text.split()[1])
        users = db.load_join_requests(message.from_user.id, -1002466466426)
        joined_users = 0
        while users_count and users:
            try:
                if msg[0].endswith('old'):
                    user_id = users.pop(0)
                else:
                    user_id = users.pop()
                print(f'Пытаюсь добавить {user_id}')
                await bot.approve_chat_join_request(-1002466466426, user_id)
                db.delete_join_request(-1002466466426, user_id)
                print(f'Добавил {user_id}')
                users_count -= 1
                joined_users += 1
            except:
                pass
        await message.answer(f'Done! Добавлено {joined_users} пользователей!')
    else:
        await message.answer('ОШИБКА! Введите команду approve и количество пользователей')
    # await bot.approve_chat_join_request(-1002466466426, user_id)


@router.channel_post(F.text == 'add_bot')
async def catch_chat_post(message: Message, bot: Bot):
    try:
        db.add_new_channel(message.from_user.id, message.chat.id)
        await bot.send_message(message.from_user.id, f'Канал {message.chat.title} успешно добавлен!')
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        await bot.send_message(message.chat.id, 'Ошибка!')


@router.channel_post(F.text == 'check')
async def catch_chat_post(message: Message, bot: Bot):
    print(db.add_join_request(message.chat.id, message.from_user.id))


@router.message(Command('amount'))
async def amount_join_requests(message: Message, bot: Bot):
    data = db.load_amount_requests_by_user(message.from_user.id)

    result = {}
    for channel, _ in data:
        channel = await bot.get_chat(channel)
        channel = channel.title
        if channel in result:
            result[channel] += 1
        else:
            result[channel] = 1

    text_msg = '\n'.join(['Ваши каналы:'] +
                         [f'{channel_id}: {users_amount}' for channel_id, users_amount in result.items()])
    await message.answer(text_msg)


def on_start():
    print('Бот запущен')


def on_shutdown():
    print('Бот отключен')


async def start_bot():
    dp.startup.register(on_start)
    dp.shutdown.register(on_start)
    db.create_tables()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
