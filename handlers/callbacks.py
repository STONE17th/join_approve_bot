from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from classes import Admin
from database.data_base import DataBase
from keyborads import inline_keyboards
from keyborads.callback_data import TestButton, RequestChannel

router = Router()
db = DataBase()


@router.callback_query(RequestChannel.filter(F.target == 'main_menu'))
async def main_menu(callback: CallbackQuery, bot: Bot):
    user = Admin(callback.from_user.id)
    message_text = f'{callback.from_user.full_name}, '
    msg = ['добавьте бота в канал для управления', 'это твои каналы:\n']
    message_text += (msg[bool(len(user.channels))] + await user.amount_requests_in_channels(bot))
    await bot.edit_message_text(
        text=message_text,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=await inline_keyboards.kb_channels_list(
            user.channels,
            bot,
        ),
    )


@router.callback_query(RequestChannel.filter(F.target == 'help'))
async def test_button(callback: CallbackQuery, callback_data: TestButton, state: FSMContext, bot: Bot) -> None:
    await callback.answer('В разработке', show_alert=True)
