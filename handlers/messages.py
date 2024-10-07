from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.filters import Command

from classes.classes import Admin, Channel
from database.data_base import DataBase
from keyborads import inline_keyboards

router = Router()
db = DataBase()


@router.message(Command('start'))
async def command_start(message: Message, bot: Bot):
    user = Admin(message.from_user.id)
    message_text = f'{message.from_user.full_name}, '
    msg = ['добавьте бота в канал для управления', 'это твои каналы:\n']
    message_text += (msg[bool(len(user.channels))] + await user.amount_requests_in_channels(bot))
    await message.answer(
        text=message_text,
        reply_markup=await inline_keyboards.kb_channels_list(user.channels, bot)
    )


@router.message(F.forward_origin)
async def catch_forward_message(message: Message, bot: Bot):
    try:
        Channel.new(message.from_user.id, message.forward_origin.chat.id)
        await bot.send_message(message.from_user.id, f'Канал {message.forward_origin.chat.title} успешно добавлен!')
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        await bot.send_message(message.chat.id, 'Ошибка!')


@router.chat_join_request()
async def new_request(message: Message, bot: Bot):
    db.add_join_request(message.chat.id, message.from_user.id)
