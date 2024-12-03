from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list

from classes import Channel
from .states import CallbackState
from keyborads.callback_data import CustomCallBack
from keyborads import inline_keyboards

router = Router()


def number_to_emoji(number: int | str) -> str:
    digits = {'0': '0️⃣',
              '1': '1️⃣',
              '2': '2️⃣',
              '3': '3️⃣',
              '4': '4️⃣',
              '5': '5️⃣',
              '6': '6️⃣',
              '7': '7️⃣',
              '8': '8️⃣',
              '9': '9️⃣'}
    return ''.join([digits[ch] for ch in str(number)])


def update_adapter(update: Message | CallbackQuery):
    if isinstance(update, Message):
        return update.from_user.id, update.message_id, update.text
    return update.from_user.id, update.message.message_id, update.message.text


@router.callback_query(CustomCallBack.filter(F.target_handler == 'control_channel'))
async def control_channel(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext, bot: Bot) -> None:
    current_state = await state.get_state()
    if not current_state:
        channel = Channel.by_tg_id(callback.from_user.id, callback_data.channel_tg_id)
        await state.update_data(
            channel=channel,
            requests=None,
            amount=0,
        )
    data = await state.get_data()
    channel = data['channel']
    auto_approve = channel.check_auto
    message_list = [
        f'Непринятых заявок в этом канале: {number_to_emoji(len(channel.requests))}',
        'Каких пользователей будем добавлять?',
        f'Автоматический прием заявок: {'✅' if channel.check_auto else '❌'}',
    ]
    if auto_approve:
        message_list.append(f'От {channel.limit.min} до {channel.limit.max} в час')
    await bot.edit_message_text(
        **as_list(*message_list).as_kwargs(),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.kb_select_approve_type(channel)
    )
    await state.set_state(CallbackState.requests_type)


@router.callback_query(CallbackState.requests_type, CustomCallBack.filter(F.target_handler == 'type_selected'))
async def select_group(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext, bot: Bot) -> None:
    message_text = {
        'new': 'Сколько новых заявок будем принимать?',
        'old': 'Сколько старых заявок будем принимать?',
        'auto': 'Сколько заявок будем принимать в час?\nВведите два целых числа'
    }
    await state.update_data(
        requests=callback_data.requests,
        amount_message_id=callback.message.message_id)
    await bot.edit_message_text(
        text=message_text[callback_data.requests],
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_keyboards.back_button(),
    )
    await state.set_state(CallbackState.requests_amount)


@router.callback_query(CallbackState.requests_type, CustomCallBack.filter(F.target_handler == 'auto_approve_stop'))
async def stop_auto_approve(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext,
                            bot: Bot) -> None:
    data = await state.get_data()
    channel = data['channel']
    amount = channel.stop_auto_approve()
    await callback.answer(
        text=f'Done!\nАвтоматический прием пользователей остановлен!\nБыло принято {number_to_emoji(amount)} заявок',
        show_alert=True,
    )
    await control_channel(callback, callback_data, state, bot)


@router.message(CallbackState.requests_amount)
async def amount_users(message: Message | CallbackQuery, state: FSMContext, bot: Bot) -> None:
    chat_id, message_id, message_text = update_adapter(message)
    requests = {
        'new': 'новых',
        'old': 'старых',
        'auto': 'Включить',
    }
    data = await state.get_data()
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    input_value = message_text.split()
    keyboard = inline_keyboards.back_button()
    correct_keyboard = inline_keyboards.kb_confirm()
    if data['requests'] in ('old', 'new'):
        message_text = f'‼️Ошибка‼️\nВы ввели: {message_text}\nТребуется ввести целое число!'
        if len(input_value) == 1:
            input_value = input_value[0]
            if input_value.isdigit() and int(input_value) > 0:
                await state.set_state(CallbackState.confirm_approve)
                await state.update_data(amount=int(input_value))
                message_text = f'Принять {number_to_emoji(input_value)} {requests[data["requests"]]} заявок?'
                keyboard = correct_keyboard
    else:
        message_text = f'‼️Ошибка‼️\nВы ввели: {message_text}\nТребуется ввести два целых числа!'
        if len(input_value) == 2:
            if all(map(lambda x: x.isdigit(), input_value)) and all(map(lambda x: int(x) > 0, input_value)):
                min_value, max_value = map(int, input_value)
                if min_value < max_value:
                    await state.set_state(CallbackState.confirm_approve)
                    await state.update_data(amount=(min_value, max_value))
                    message_text = f'Запустить автоматический прием от {number_to_emoji(min_value)} до {number_to_emoji(max_value)} в час?'
                    keyboard = correct_keyboard
                else:
                    message_text = (f'‼️Ошибка‼️\nВы ввели: {message_text}\n'
                                    f'Минимальный предел должен быть меньше либо равен максимальному!')
    await bot.edit_message_text(
        text=message_text,
        chat_id=chat_id,
        message_id=data['amount_message_id'],
        reply_markup=keyboard,
    )


@router.callback_query(CallbackState.confirm_approve, CustomCallBack.filter(F.target_handler == 'confirm_approve'))
async def confirm_requests(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext, bot: Bot):
    data = await state.get_data()
    channel = data['channel']
    amount = data['amount']
    if data['requests'] in ('old', 'new'):
        joined_users = 0
        while amount and channel.requests:
            if await channel.get_request(data['requests'] == 'new').approve(bot):
                joined_users += 1
            amount -= 1
        await callback.answer(f'Done!\nДобавлено {number_to_emoji(joined_users)} пользователей!', show_alert=True)
    else:
        channel.set_limits(amount)
        await channel.start_auto_approve(amount, bot)
        await callback.answer(f'Done!\nАвтоматический прием пользователей запущен!', show_alert=True)
    await control_channel(callback, callback_data, state, bot)


@router.callback_query(CallbackState(), CustomCallBack.filter(F.target_handler == 'back'))
async def back_button_handler(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext, bot: Bot):
    current_state = await state.get_state()
    if current_state == CallbackState.requests_amount:
        await state.set_state(CallbackState.target_channel)
        await control_channel(callback, callback_data, state, bot)
    elif current_state == CallbackState.confirm_approve:
        await state.set_state(CallbackState.requests_amount)
        await control_channel(callback, callback_data, state, bot)
