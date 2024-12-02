from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, Bold

from classes import Admin, Channel
from database.data_base import DataBase
from .states import CallbackState
from keyborads.callback_data import CustomCallBack
from keyborads import inline_keyboards

router = Router()


def update_adapter(update: Message | CallbackQuery):
    if isinstance(update, Message):
        return update.from_user.id, update.message_id, update.text
    return update.from_user.id, update.message.message_id, update.message.text


# async def delete_message(chat_id: int, message_id: int, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     if not data['back']:
#         await bot.delete_message(
#             chat_id=chat_id,
#             message_id=message_id,
#         )
#     await state.update_data(back=False)

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
    print(f'Выбирает {channel.title}')
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
        reply_markup=inline_keyboards.kb_select_approve_type(channel)
    )
    # if auto_approve:
    await state.set_state(CallbackState.requests_type)
    # else:
    #     await state.set_state(CallbackState.cancel_auto_approve)


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
    user_data = await state.get_data()
    print(message_text[callback_data.requests])
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
    channel.stop_auto_approve()
    print('Остановил автоотправку')
    await callback.answer(
        text=f'Done!\nАвтоматический прием пользователей остановлен!',
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
    # print(data['back'])
    # await delete_message(
    #     chat_id=chat_id,
    #     message_id=message_id,
    #     state=state,
    #     bot=bot,
    # )
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    # await bot.delete_message(
    #     chat_id=message.chat.id,
    #     message_id=message.message_id,
    # )
    # if message_text:
    print(data['requests'], message_text)
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
                message_text = f'Принять {input_value} {requests[data["requests"]]} заявок?'
                keyboard = correct_keyboard
    else:
        message_text = f'‼️Ошибка‼️\nВы ввели: {message_text}\nТребуется ввести два целых числа!'
        if len(input_value) == 2:
            if all(map(lambda x: x.isdigit(), input_value)) and all(map(lambda x: int(x) > 0, input_value)):
                min_value, max_value = map(int, input_value)
                if min_value < max_value:
                    await state.set_state(CallbackState.confirm_approve)
                    await state.update_data(amount=(min_value, max_value))
                    message_text = f'Запустить автоматический прием от {min_value} до {max_value} в час?'
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
        await callback.answer(f'Done!\nДобавлено {joined_users} пользователей!', show_alert=True)
        print(f'Принято {joined_users}')
    else:
        channel.set_limits(amount)
        channel.start_auto_approve(amount, bot)
        await callback.answer(f'Done!\nАвтоматический прием пользователей запущен!', show_alert=True)
        print('Запущен прием автоматический')
    await control_channel(callback, callback_data, state, bot)


@router.callback_query(CallbackState(), CustomCallBack.filter(F.target_handler == 'back'))
async def back_button_handler(callback: CallbackQuery, callback_data: CustomCallBack, state: FSMContext, bot: Bot):
    # await state.update_data(back=True)
    current_state = await state.get_state()
    # await callback.answer(str(current_state), show_alert=True)
    if current_state == CallbackState.requests_amount:
        await state.set_state(CallbackState.target_channel)
        await control_channel(callback, callback_data, state, bot)
    elif current_state == CallbackState.confirm_approve:
        await state.set_state(CallbackState.requests_amount)
        await control_channel(callback, callback_data, state, bot)
    # data = await state.get_data()
    # channel = data['channel']
    # amount = data['amount']
    # if data['requests'] in ('old', 'new'):
    #     joined_users = 0
    #     while amount and channel.requests:
    #         if await channel.get_request(data['requests'] == 'new').approve(bot):
    #             joined_users += 1
    #         amount -= 1
    #     await callback.answer(f'Done!\nДобавлено {joined_users} пользователей!', show_alert=True)
    # else:
    #     channel.set_limits(amount)
    #     channel.start_auto_approve(amount, bot)
    #     await callback.answer(f'Done!\nАвтоматический прием пользователей запущен!', show_alert=True)
    # await control_channel(callback, callback_data, state, bot)
