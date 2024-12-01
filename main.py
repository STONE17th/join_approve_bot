import os
import asyncio

from aiogram import Bot, Dispatcher

from database.data_base import DataBase
from fsm import router as fsm_router
from handlers import main_router

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

dp.include_routers(
    main_router,
    fsm_router,
)


def on_start():
    print('Bot is started...')
    print('DataBase connection:', end=' ')
    try:
        DataBase().create_tables()
        print('OK!')
    except Exception as e:
        print('Failure!!')
        print(e)


def on_shutdown():
    print('Бот отключен')


async def start_bot():
    dp.startup.register(on_start)
    dp.shutdown.register(on_start)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
