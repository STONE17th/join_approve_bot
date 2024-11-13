from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from random import randint

from classes import Channel, Request

bot_scheduler = AsyncIOScheduler()


# async def approve_request(channel: Channel, bot: Bot):
#     await channel.get_request(new=False).approve(bot)
#
#
# async def approve_requests_at_time(channel: Channel, min_amount: int, max_amount: int, timedelta: int, bot: Bot):
#     job_id = f'{channel.channel_tg_id}'
#     while channel.requests:
#         requests_amount = randint(min_amount, max_amount)
#         request_per_once = timedelta // requests_amount
#         if bot_scheduler.:
#             bot_scheduler.reschedule_job(f'{trainer.tg_id}', trigger='cron', hour=hours, minute=minutes)
#         else:
#             bot_scheduler.add_job(func=approve_request,
#                                   id=job_id,
#                                   trigger='cron',
#                                   args=[channel, bot],
#                                   hour=request_per_once // 60,
#                                   minute=request_per_once % 60,
#                                   )
#         await asyncio.sleep(timedelta)
#
#
# async def notify_trainer(bot: Bot, trainer: Trainer):
#     athletes_list = TrainingsDB().not_training_today(trainer.id)
#     message_text = f'Привет, {trainer.first_name}!\nПришло время отметить тех, кто был сегодня на тренировке:'
#     if athletes_list:
#         await bot.send_photo(chat_id=trainer.tg_id, photo=trainer.photo,
#                              caption=message_text,
#                              reply_markup=ikb_athletes_list(trainer))
#
#
# async def add_notification(bot: Bot, trainer: Trainer):
#     hours, minutes = list(map(int, [trainer.options.schedule_time[:2], trainer.options.schedule_time[2:]]))
#     bot_scheduler.add_job(notify_trainer, 'cron', hour=hours, minute=minutes,
#                           id=f'{trainer.tg_id}', args=[bot, trainer])
#
#
# async def modify_notification(trainer: Trainer):
#     hours, minutes = list(map(int, [trainer.options.schedule_time[:2], trainer.options.schedule_time[2:]]))
#     print(hours, minutes)
#     bot_scheduler.reschedule_job(f'{trainer.tg_id}', trigger='cron', hour=hours, minute=minutes)
#
#
# async def start_scheduler(bot: Bot):
#     for trainer in [Trainer(user[1]) for user in TrainersDB().load_all()]:
#         await add_notification(bot, trainer)
#     bot_scheduler.start()
#     bot_scheduler.shutdown()
