from aiogram import Bot, F, Router
from aiogram.types import Message

from database.data_base import DataBase

router = Router()
db = DataBase()


@router.chat_join_request()
async def incoming_join_request(message: Message, bot: Bot):
    db.add_join_request(message.chat.id, message.from_user.id)
    await bot.send_message(409205647, str(message.from_user.id))
    # await bot.send_message(409205647, str(message.chat.id))
