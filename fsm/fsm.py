from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, Bold

from classes import Admin
from database.data_base import DataBase
from .states import CallbackState
from keyborads.callback_data import RequestChannel
from keyborads import inline_keyboards

router = Router()


# db = DataBase()


@router.callback_query(RequestChannel.filter(F.target == 'select_channel'))
async def select_channel(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot) -> None:
    admin_user = Admin(callback.from_user.id)
    current_state = await state.get_state()
    if not current_state:
        await state.update_data(
            admin_tg_id=callback.from_user.id,
            channel_tg_id=callback_data.channel_tg_id
        )
    data = await state.get_data()
    channel_tg_id = data['channel_tg_id']
    channel = admin_user.channels[channel_tg_id]
    auto_approve = channel.check_auto
    message_list = [
        f'Непринятых заявок в этом канале: {len(channel.requests)}',
        'Каких пользователей будем добавлять?',
        f'Автоматический прием заявок: {'✅' if channel.check_auto else '❌'}',
    ]
    if auto_approve:
        message_list.append(f'От {channel.limits.min} до {channel.limits.max} в час')
    await bot.edit_message_text(
        **as_list(*message_list).as_kwargs(),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_select_option(channel)
    )
    if auto_approve:
        await state.set_state(CallbackState.auto_stop)
    else:
        await state.set_state(CallbackState.channel_tg_id)


@router.callback_query(CallbackState.channel_tg_id, RequestChannel.filter(F.target == 'select_option'))
async def select_group(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot) -> None:
    message_text = {
        'new': 'Сколько новых заявок будем принимать?',
        'old': 'Сколько старых заявок будем принимать?',
        'auto': 'Сколько заявок будем принимать в час?\nВведите два целых числа'
    }
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


@router.callback_query(CallbackState.auto_stop, RequestChannel.filter(F.target == 'select_option'))
async def stop_auto_approve(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext,
                            bot: Bot) -> None:
    admin_user = Admin(callback.from_user.id)
    data = await state.get_data()
    channel_tg_id = data['channel_tg_id']
    # await state.update_data(
    #     admin_tg_id=callback_data.admin_tg_id,
    #     channel_tg_id=callback_data.channel_tg_id
    # )
    channel = admin_user.channels[channel_tg_id]
    channel.stop_auto_approve()
    await callback.answer(
        text=f'Done!\nАвтоматический прием пользователей остановлен!',
        show_alert=True,
    )
    # await state.clear()
    await select_channel(callback, callback_data, state, bot)


@router.message(CallbackState.group)
async def amount_users(message: Message, state: FSMContext, bot: Bot) -> None:
    requests = {
        'new': 'новых',
        'old': 'старых',
        'auto': 'Включить',
    }
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    input_value = message.text.split()
    keyboard = inline_keyboards.back_button(
        data['admin_tg_id'],
        data['channel_tg_id'],
        'select_channel',
    )
    correct_keyboard = inline_keyboards.kb_confirm(
        channel_tg_id=data['channel_tg_id'],
        admin_tg_id=data['admin_tg_id'],
    )
    if data['index'] in ('old', 'new'):
        message_text = f'‼️Ошибка‼️\nВы ввели: {message.text}\nТребуется ввести целое число!'
        if len(input_value) == 1:
            input_value = input_value[0]
            if input_value.isdigit() and int(input_value) > 0:
                await state.set_state(CallbackState.confirm)
                await state.update_data(amount=int(input_value))
                message_text = f'Принять {input_value} {requests[data["index"]]} заявок?'
                keyboard = correct_keyboard
    else:
        message_text = f'‼️Ошибка‼️\nВы ввели: {message.text}\nТребуется ввести два целых числа!'
        if len(input_value) == 2:
            if all(map(lambda x: x.isdigit(), input_value)) and all(map(lambda x: int(x) > 0, input_value)):
                min_value, max_value = map(int, input_value)
                if min_value < max_value:
                    await state.set_state(CallbackState.confirm)
                    await state.update_data(amount=(min_value, max_value))
                    message_text = f'Запустить автоматический прием от {min_value} до {max_value} в час?'
                    keyboard = correct_keyboard
                else:
                    message_text = (f'‼️Ошибка‼️\nВы ввели: {message.text}\n'
                                    f'Минимальный предел должен быть меньше либо равен максимальному!')
    await bot.edit_message_text(
        text=message_text,
        chat_id=message.chat.id,
        message_id=data['amount_message_id'],
        reply_markup=keyboard,
    )


@router.callback_query(CallbackState.confirm, RequestChannel.filter(F.target == 'confirm_approve'))
async def confirm_requests(callback: CallbackQuery, callback_data: RequestChannel, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_admin = Admin(data['admin_tg_id'])
    channel = user_admin.channels[data['channel_tg_id']]
    amount = data['amount']
    if data['index'] in ('old', 'new'):

        joined_users = 0

        while amount and channel.requests:
            if await channel.get_request(data['index'] == 'new').approve(bot):
                joined_users += 1
            amount -= 1
        await callback.answer(f'Done!\nДобавлено {joined_users} пользователей!', show_alert=True)
    else:
        channel.set_limits(amount)
        channel.start_auto_approve(amount, bot)
        await callback.answer(f'Done!\nАвтоматический прием пользователей запущен!', show_alert=True)
    await select_channel(callback, callback_data, state, bot)
