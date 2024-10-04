from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.data_base import DataBase
from .states import CallbackState
from keyborads.callback_data import NewOrOld, ConfirmCallback, BackButton, RequestChannel
from keyborads import inline_keyboards

router = Router()
db = DataBase()


@router.callback_query(RequestChannel.filter(F.target == 'select_channel'))
async def select_channel(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot) -> None:
    await state.set_state(CallbackState.channel_tg_id)
    print(db.load_amount_requests_in_channel(callback_data.channel_tg_id))
    await state.update_data(admin_tg_id=callback_data.admin_tg_id, channel_tg_id=callback_data.channel_tg_id)
    await bot.edit_message_text(
        'Каких пользователей будем добавлять?',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_new_or_old()
    )


@router.callback_query(CallbackState.channel_tg_id, NewOrOld.filter(F.button == 'new_old'))
async def new_or_old_selection(callback: CallbackQuery, callback_data: NewOrOld, state: FSMContext, bot: Bot) -> None:
    data = 0 if callback_data.value == 'new' else -1
    await state.update_data(index=data, amount_message_id=callback.message.message_id)
    user_data = await state.get_data()
    await bot.edit_message_text(
        f'Сколько будем {'старых' if data else 'новых'} добавлять?',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.back_button(
            user_data['admin_tg_id'],
            user_data['channel_tg_id'],
            'select_channel',
        )
    )
    await state.set_state(CallbackState.group)


@router.message(CallbackState.group)
async def amount_users(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text.isdigit():
        await state.update_data(amount=int(message.text))
        await state.set_state(CallbackState.confirm)
        await bot.edit_message_text(
            f'Добавить {message.text} {'старых' if data['index'] else 'новых'} заявок?',
            chat_id=message.chat.id,
            message_id=data['amount_message_id'],
            reply_markup=inline_keyboards.kb_confirm()
        )
    else:
        await bot.edit_message_text(
            f'Ошибка! {message.text}\nТребуется ввести целое положительное число!',
            chat_id=message.chat.id,
            message_id=data['amount_message_id'],
            reply_markup=inline_keyboards.back_button(
                data['admin_tg_id'],
                data['channel_tg_id'],
                'select_channel',
            )
        )


@router.callback_query(CallbackState.confirm, ConfirmCallback.filter(F.button == 'confirm_join'))
async def confirm_requests(callback: CallbackQuery, callback_data: ConfirmCallback, state: FSMContext, bot: Bot):
    if callback_data.value == 'yes':
        data = await state.get_data()
        index = data['index']
        amount = data['amount']
        admin_tg_id = data['admin_tg_id']
        channel_tg_id = data['channel_tg_id']
        users = db.load_join_requests(channel_tg_id)
        joined_users = 0
        while amount and users:
            if index:
                user_id = users.pop(0)
            else:
                user_id = users.pop()
            try:
                await bot.approve_chat_join_request(channel_tg_id, user_id)
                db.delete_join_request(channel_tg_id, user_id)
                print(f'Добавил {user_id}')
                amount -= 1
                joined_users += 1
            except:
                pass
        await callback.answer(f'Done! Добавлено {joined_users} пользователей!', show_alert=True)
    else:
        # await state.set_state(UserState.name)
        # await new_user_name(callback, state, bot)
        pass
    await state.clear()

# @router.callback_query(BackButton.filter(F.button == 'back_button'))
# async def back_button(callback: CallbackQuery, callback_data: BackButton, state: FSMContext, bot: Bot):
#     print(callback_data.menu)
#     match callback_data.menu:
#         case 'amount':
#             await callback.answer('В разработке!', show_alert=False)
#             await select_channel(callback, callback_data, state, bot)

#
#
# @user_registration_fsm_router.message(UserState.address)
# async def new_user_address(message: Message, state: FSMContext, bot: Bot) -> None:
#     await state.update_data(address=message.text)
#     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     data = await state.get_data()
#     cur_chat = data['cur_chat']
#     cur_message = data['cur_message']
#     caption = f'{data["name"]}\n{data["phone"]}\n{data["address"]}\n\nДанные введены верно?'
#     photo = InputMediaPhoto(media=pict.get('reg'), caption=caption)
#     await state.set_state(UserState.confirm)
#     await bot.edit_message_media(photo, cur_chat, cur_message, reply_markup=ikb_confirm('new_user'))
#
