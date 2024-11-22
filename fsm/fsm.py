from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, Bold

from classes import Admin
from database.data_base import DataBase
from .states import CallbackState
from keyborads.callback_data import ConfirmCallback, NewOrOld, RequestChannel
from keyborads import inline_keyboards

router = Router()


# db = DataBase()


@router.callback_query(RequestChannel.filter(F.target == 'select_channel'))
async def select_channel(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot) -> None:
    admin_user = Admin(callback.from_user.id)
    await state.set_state(CallbackState.channel_tg_id)
    await state.update_data(
        admin_tg_id=callback_data.admin_tg_id,
        channel_tg_id=callback_data.channel_tg_id
    )
    channel = admin_user.channels[callback_data.channel_tg_id]
    caption = as_list(
        f'Непринятых заявок в этом канале: {len(channel.requests)}',
        'Каких пользователей будем добавлять?',
        f'Автоматический прием заявок: {'✅' if channel.check_auto else '❌'}',
        f'От {channel.min_requests} до {channel.max_requests} в час' if channel.check_auto else '',
    )
    await bot.edit_message_text(
        **caption.as_kwargs(),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_select_option(channel)
    )


@router.callback_query(CallbackState.channel_tg_id, NewOrOld.filter(F.button == 'select_option'))
async def select_group(callback: CallbackQuery, callback_data: NewOrOld, state: FSMContext, bot: Bot) -> None:
    message_text = {
        'new': 'Сколько новых заявок будем принимать?',
        'old': 'Сколько старых заявок будем принимать?',
        'auto': 'Сколько заявок будем принимать в час?\nВведите два целых числа'
    }
    # if callback_data.value == 'new':
    #     msg_users = 'новых'
    # elif callback_data.value == 'old':
    #     msg_users = 'старых'
    # else:
    #     msg_users = 'рандомных'
    await state.update_data(index=callback_data.value, amount_message_id=callback.message.message_id)
    user_data = await state.get_data()
    await bot.edit_message_text(
        text=message_text[callback_data.value],
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
    requests = {
        'new': 'новых',
        'old': 'старых',
    }
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text.isdigit() and int(message.text) > 0:
        await state.update_data(amount=int(message.text))
        await state.set_state(CallbackState.confirm)
        await bot.edit_message_text(
            text=f'Принять {message.text} {requests[data["index"]]} заявок?',
            chat_id=message.chat.id,
            message_id=data['amount_message_id'],
            reply_markup=inline_keyboards.kb_confirm(
                channel_tg_id=data['channel_tg_id'],
                admin_tg_id=data['admin_tg_id'],
            ),
        )
    else:
        await bot.edit_message_text(
            f'‼️Ошибка‼️\nВведено: {message.text}\nТребуется ввести целое положительное число!',
            chat_id=message.chat.id,
            message_id=data['amount_message_id'],
            reply_markup=inline_keyboards.back_button(
                data['admin_tg_id'],
                data['channel_tg_id'],
                'select_channel',
            )
        )


@router.callback_query(CallbackState.confirm, RequestChannel.filter(F.target == 'confirm_approve'))
async def confirm_requests(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot):

    data = await state.get_data()
    index = data['index']
    amount = data['amount']
    admin_tg_id = data['admin_tg_id']
    channel_tg_id = data['channel_tg_id']
    user_admin = Admin(admin_tg_id)
    joined_users = 0
    channel = user_admin.channels[channel_tg_id]
    while amount and channel.requests:
        if await channel.get_request(index == 'new').approve(bot):
            joined_users += 1
        amount -= 1
    # await bot.edit_message_text(
    #     chat_id=callback.from_user.id,
    #     message_id=callback.message.message_id,
    #     text=
    # )
    await callback.answer(f'Done! Добавлено {joined_users} пользователей!', show_alert=True)
    await state.clear()
    await select_channel(callback, callback_data, state, bot)
