import os
import asyncio

from aiogram import Bot, Dispatcher, Router

from database.data_base import DataBase
from fsm import router as fsm_router
import handlers

bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_routers(
    handlers.callbacks_router,
    handlers.messages_router,
    fsm_router,
)


def on_start():
    print('Bot is started...')
    print('DataBase connection:', end=' ')
    try:
        DataBase().create_tables()
        print('OK!')
    except:
        print('Failure!!')


def on_shutdown():
    print('Бот отключен')


async def start_bot():
    dp.startup.register(on_start)
    dp.shutdown.register(on_start)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
