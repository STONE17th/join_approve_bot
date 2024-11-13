import asyncio

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from random import randint

from database.data_base import DataBase


class Request:
    db = DataBase()

    def __init__(self, channel_tg_id: int, request_tg_id: int):
        self.channel_tg_id = channel_tg_id
        self.request_tg_id = request_tg_id

    async def approve(self, bot: Bot):
        Request.db.delete_request(self.channel_tg_id, self.request_tg_id)
        try:
            await bot.approve_chat_join_request(
                chat_id=self.channel_tg_id,
                user_id=self.request_tg_id,
            )
            return True
        except Exception as e:
            print(f'Не удалось добавить {self.request_tg_id}')
            return False

    def test(self):
        print(self.request_tg_id)
        Request.db.delete_request(self.channel_tg_id, self.request_tg_id)


class Channel:
    db = DataBase()
    _bot_scheduler = AsyncIOScheduler()

    # def __new__(cls, *args, **kwargs):
    #     if Channel._bot_scheduler is None:
    #         Channel._bot_scheduler = AsyncIOScheduler()

    def __init__(self, channel_tg_id: int, admin_tg_id: int):
        self.channel_tg_id = channel_tg_id
        self.admin_tg_id = admin_tg_id
        self._requests = None
        self.scheduler: AsyncIOScheduler | None = None

    @property
    def requests(self):
        if self._requests is None:
            self._requests = [Request(self.channel_tg_id, request_tg_id)
                              for request_tg_id in self.db.load_requests(self.channel_tg_id)]
        return self._requests

    async def title(self, bot: Bot):
        channel = await bot.get_chat(self.channel_tg_id)
        return channel.title

    def get_request(self, new: bool) -> Request:
        if self.requests:
            return self.requests.pop() if new else self.requests.pop(0)

    async def test_approve(self, request_count: tuple[int, int]):
        requests = randint(*request_count)
        for _ in range(requests):
            time_pause = 60 // requests - 1
            await asyncio.sleep(time_pause)
            if self.requests:
                self.get_request(new=False).test()
            else:
                Channel._bot_scheduler.remove_job(f'{self.channel_tg_id}')
                # self.stop_auto_approve()
                break

    # async def auto_approve(self, min_count: int, max_count: int):
    #     while True:
    #
    #         Channel._bot_scheduler.add_job(
    #             func=self.start_auto_approve,
    #             id=f'timer_{self.channel_tg_id}',
    #             trigger='interval',
    #             hours=1,
    #             args=[(min_count, max_count)]
    #         )
    #         if not Channel._bot_scheduler.running:
    #             Channel._bot_scheduler.start()
    #         await asyncio.sleep(60)
    #         Channel._bot_scheduler.remove_job(job_id=f'timer_{self.channel_tg_id}')

    def start_auto_approve(self, time_delta: tuple[int, int]):
        Channel._bot_scheduler.add_job(
            func=self.test_approve,
            id=f'{self.channel_tg_id}',
            trigger='interval',
            seconds=60,
            args=[time_delta],
        )
        if not Channel._bot_scheduler.running:
            Channel._bot_scheduler.start()

    def stop_auto_approve(self):
        if Channel._bot_scheduler.get_job(job_id=f'{self.channel_tg_id}'):
            Channel._bot_scheduler.remove_job(job_id=f'{self.channel_tg_id}')
        # Channel._bot_scheduler.remove_job(job_id=f'timer_{self.channel_tg_id}')
        if not Channel._bot_scheduler.get_jobs():
            Channel._bot_scheduler.shutdown()


class Admin:
    db = DataBase()

    def __init__(self, admin_tg_id: int):
        self.admin_tg_id = admin_tg_id
        self._channels = None

    @property
    def channels(self):
        return {int(channel_tg_id[0]): Channel(channel_tg_id[0], self.admin_tg_id)
                for channel_tg_id in self.db.load_channels(self.admin_tg_id)}
