from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.data_base import DataBase
from keyborads import inline_keyboards
from keyborads.callback_data import TestButton, RequestChannel
from fsm.states import CallbackState
from .messages import amount_join_requests

router = Router()
db = DataBase()


@router.callback_query(RequestChannel.filter(F.target == 'main_menu'))
async def main_menu(callback: CallbackQuery, bot: Bot):
    channels = []
    for channel_tg_id in db.load_admin_channels(callback.from_user.id):
        channel = await bot.get_chat(channel_tg_id)
        channels.append((channel.title, channel_tg_id))
    await bot.edit_message_text(
        text=await amount_join_requests(
            callback.from_user.full_name,
            callback.from_user.id,
            bot
        ) + '\n\nВыберите канал для управления:',
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_channels_list(
            callback.from_user.id,
            channels
        )
    )


@router.callback_query(RequestChannel.filter(F.target == 'help'))
async def test_button(callback: CallbackQuery, callback_data: TestButton, state: FSMContext, bot: Bot) -> None:
    await callback.answer('В разработке', show_alert=True)
#
#
# @router.callback_query(RequestChannel.filter(F.target == 'select_channel'))
# async def select_channel(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot) -> None:
#     print('Here')
#     await state.set_state(CallbackState.channel_tg_id)
#     # data = list(map(int, callback.data.split(':')[2:]))
#     # print(data)
#     await state.update_data(admin_tg_id=callback_data.admin_tg_id, channel_tg_id=callback_data.channel_tg_id)
#     await bot.edit_message_text(
#         'Каких пользователей будем добавлять?',
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         reply_markup=inline_keyboards.kb_new_or_old()
#     )
