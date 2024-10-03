from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from .states import CallbackState
from keyborads.callback_data import AdminChannel, NewOrOld
from keyborads import inline_keyboards

router = Router()


@router.callback_query(AdminChannel.filter(F.button == 'start'))
async def select_channel(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.set_state(CallbackState.channel_tg_id)
    data = list(map(int, callback.data.split(':')[2:]))
    print(data)
    await state.update_data(admin_tg_id=data[0], channel_tg_id=data[1])
    await bot.edit_message_text(
        'TEST MESSAGE',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_new_or_old()
    )


@router.callback_query(CallbackState.channel_tg_id, NewOrOld.filter(F.button == 'new_old'))
async def new_or_old_selection(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = 0 if callback.data.split(':')[-1] == 'new' else -1
    await state.update_data(index=data)
    await bot.edit_message_text(
        f'Сколько будем {'старых' if data else 'новых'} добавлять?',
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )
    await state.set_state(CallbackState.group)


@router.message(CallbackState.group)
async def amount_users(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text.isdigit():
        await state.update_data(amount=int(message.text))
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        data = state.get_data()
        await bot.edit_message_text(
            f'Добавить {data['amount']} {'старых' if data['index'] else 'новых'} заявок?',
            chat_id=message.chat.id,
            message_id=message.message_id
        )
        await state.set_state(CallbackState.confirm)
    else:
        await bot.edit_message_text(
            f'Ошибка! {message.text}\nТребуется ввести целое положительное число!',
            chat_id=message.chat.id,
            message_id=message.message_id
        )

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
#
# @user_registration_fsm_router.callback_query(UserState.confirm, ConfirmCB.filter(F.menu == 'new_user'))
# async def new_user_confirm(callback: CallbackQuery, callback_data: ConfirmCB, state: FSMContext, bot: Bot) -> None:
#     if callback_data.button == 'yes':
#         data = await state.get_data()
#         cur_chat = data['cur_chat']
#         cur_message = data['cur_message']
#         user_data = callback.from_user.id, data['name'], data['phone'], data['address'], 0, 1
#         User.create(user_data)
#         photo = InputMediaPhoto(media=pict.get('main'), caption='Вы успешно зарегистрированы в системе!')
#         await bot.edit_message_media(photo, cur_chat, cur_message, reply_markup=ikb_select_type(user_data[0], 'main'))
#         await state.clear()
#     else:
#         await state.set_state(UserState.name)
#         await new_user_name(callback, state, bot)
