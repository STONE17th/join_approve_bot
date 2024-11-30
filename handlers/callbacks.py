from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from classes import Admin
from database.data_base import DataBase
from fsm.states import CallbackState
from keyborads import inline_keyboards
from keyborads.callback_data import RequestChannel

router = Router()
db = DataBase()


@router.callback_query(CallbackState(), RequestChannel.filter(F.target == 'main_menu'))
async def main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    admin = Admin(callback.from_user.id)
    message_text = f'{callback.from_user.full_name}, '
    channels_list = []
    if admin.channels:
        message_text += 'это твои каналы:\n'
        for channel in admin.channels.values():
            channel_title = await channel.title(bot)
            channels_list.append((channel_title, channel))
            message_text += f'{channel_title}: {len(channel.requests)} заявок\n'
    else:
        message_text += 'добавьте бота в канал для управления'
    await bot.edit_message_text(
        text=message_text,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_channels_list(channels_list),
    )

# @router.callback_query(RequestChannel.filter(F.target == 'help'))
# async def test_button(callback: CallbackQuery, callback_data: TestButton, state: FSMContext, bot: Bot) -> None:
#     await callback.answer('В разработке', show_alert=True)
