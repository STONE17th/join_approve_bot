from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from classes.classes import Admin, Channel
from database.data_base import DataBase
from keyborads import inline_keyboards
from keyborads.callback_data import RequestChannel

router = Router()
db = DataBase()


async def amount_join_requests(admin_name: str, admin_tg_id: int, bot: Bot) -> str:
    data = db.load_amount_requests_by_user(admin_tg_id)
    result = {}
    for channel, _ in data:
        channel = await bot.get_chat(channel)
        channel = channel.title
        if channel in result:
            result[channel] += 1
        else:
            result[channel] = 1
    return '\n'.join([f'{admin_name}, Ваши каналы и количество заявок на данный момент:'] +
                     [f'{channel_id}: {users_amount}' for channel_id, users_amount in result.items()])


@router.message(Command('test'))
async def com_add(message: Message, bot: Bot):
    user = Admin(message.from_user.id)
    text = await user.requests_in_channels
    await message.answer(text)


@router.message(Command('start'))
async def command_start(message: Message, bot: Bot):
    user = Admin(message.from_user.id, bot)
    if await user.channels:
        message_text = f'{message.from_user.full_name}, это твои каналы:\n' + await user.requests_in_channels
    # channels = []
    # for channel_tg_id in db.load_admin_channels(message.from_user.id):
    #     channel = await bot.get_chat(channel_tg_id)
    #     channels.append((channel.title, channel_tg_id))
    # if channels:
    #     message_text = await amount_join_requests(
    #         message.from_user.full_name,
    #         message.from_user.id,
    #         bot,
    #     ) + '\n\nВыберите канал для управления:'
    else:
        message_text = f'{message.from_user.full_name}, добавьте бота в канал для управления'
    await message.answer(
        text=message_text,
        reply_markup=await inline_keyboards.kb_channels_list(await user.channels)
    )


# @router.message(F.text.startswith('approve'))
# async def approve_incoming_user(message: Message, bot: Bot):
#     msg = message.text.split()
#     if len(msg) == 2 and msg[1].isdigit() and (msg[0].endswith('old') or msg[0].endswith('new')):
#         users_count = int(message.text.split()[1])
#         users = db.load_join_requests(message.from_user.id, -1002466466426)
#         joined_users = 0
#         while users_count and users:
#             try:
#                 if msg[0].endswith('old'):
#                     user_id = users.pop(0)
#                 else:
#                     user_id = users.pop()
#                 print(f'Пытаюсь добавить {user_id}')
#                 await bot.approve_chat_join_request(-1002466466426, user_id)
#                 db.delete_join_request(-1002466466426, user_id)
#                 print(f'Добавил {user_id}')
#                 users_count -= 1
#                 joined_users += 1
#             except:
#                 pass
#         await message.answer(f'Done! Добавлено {joined_users} пользователей!')
#     else:
#         await message.answer('ОШИБКА! Введите команду approve и количество пользователей')


@router.channel_post(F.text == 'add_bot')
async def catch_chat_post(message: Message, bot: Bot):
    try:
        Channel.new(message.from_user.id, message.chat.id)
        await bot.send_message(message.from_user.id, f'Канал {message.chat.title} успешно добавлен!')
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        await bot.send_message(message.chat.id, 'Ошибка!')
