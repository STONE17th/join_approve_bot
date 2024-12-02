from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list

from classes import Admin
from database.data_base import DataBase
from fsm.states import CallbackState
from keyborads import inline_keyboards
from keyborads.callback_data import CustomCallBack

router = Router()
db = DataBase()


@router.callback_query(CallbackState(), CustomCallBack.filter(F.target_handler == 'main_menu'))
async def main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    admin = Admin(callback.from_user.id)
    caption = as_list(
        f'{callback.from_user.full_name}, приветствую тебя!',
        'Выбери канал для управления',
    )
    keyboard = inline_keyboards.kb_channels_list(admin)
    await bot.edit_message_text(
        **caption.as_kwargs(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )
