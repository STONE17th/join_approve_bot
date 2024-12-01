import asyncio

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime
from random import randint

from classes.scheduler import Scheduler
from database.data_base import DataBase


class Request:
    _db = DataBase()

    def __init__(self, channel_tg_id: int, request_tg_id: int, creation_date: datetime):
        self.channel_tg_id = channel_tg_id
        self.request_tg_id = request_tg_id
        self.creation_date = creation_date

    async def approve(self, bot: Bot):
        self._db.delete_request(self.channel_tg_id, self.request_tg_id)
        try:
            await bot.approve_chat_join_request(
                chat_id=self.channel_tg_id,
                user_id=self.request_tg_id,
            )
            return True
        except Exception as e:
            return False

    def __eq__(self, other):
        return self.request_tg_id == other.request_tg_id

    def __str__(self):
        # return f'{self.request_tg_id:>15} {self.creation_date:<15}'
        return f'{self.request_tg_id}'

    # def test(self):
    #     # print(self.request_tg_id)
    #     Request._db.delete_request(self.channel_tg_id, self.request_tg_id)


class Channel:
    db = DataBase()
    _bot_scheduler = Scheduler()

    # def __new__(cls, *args, **kwargs):
    #     if Channel._bot_scheduler is None:
    #         Channel._bot_scheduler = AsyncIOScheduler()

    def __init__(self, channel_tg_id: int, admin_tg_id: int):
        self.channel_tg_id = channel_tg_id
        self.admin_tg_id = admin_tg_id
        self._requests: list[Request] | None = None
        self.limits = Limits(admin_tg_id, channel_tg_id)

    @property
    def requests(self) -> list[Request]:
        if self._requests is None:
            request_list = [Request(self.channel_tg_id, *request) for request in
                            self.db.load_requests(self.channel_tg_id)]
            self._requests = sorted(request_list, key=lambda x: x.creation_date)
            # self._requests = request_list
        return self._requests

    def set_limits(self, values: tuple[int, int]):
        print(values)
        DataBase().set_admin_limits(self.admin_tg_id, self.channel_tg_id, *values)

    async def title(self, bot: Bot):
        channel = await bot.get_chat(self.channel_tg_id)
        return channel.title

    def get_request(self, new: bool) -> Request:
        if self.requests:
            return self.requests.pop() if new else self.requests.pop(0)

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

    @property
    def check_auto(self) -> bool:
        return bool(self._bot_scheduler.get_job(f'{self.channel_tg_id}'))

    def _stop_job(self):
        self._bot_scheduler.remove_job(job_id=f'{self.channel_tg_id}')
        # self.min_requests, self.max_requests = 0, 0

    def start_auto_approve(self, time_delta: tuple[int, int], bot: Bot):
        self.limits.min, self.limits.max = time_delta
        self._bot_scheduler.add_job(
            func=self.auto_approve,
            args=(bot,),
            id=f'{self.channel_tg_id}',
            trigger='interval',
            seconds=60,
        )
        if not self._bot_scheduler.running:
            self._bot_scheduler.start()

    def stop_auto_approve(self):
        if self.check_auto:
            self._stop_job()
        if not self._bot_scheduler.get_jobs():
            self._bot_scheduler.shutdown()

    async def auto_approve(self, bot: Bot):
        requests = randint(self.limits.min, self.limits.max)
        time_pause = 60 // requests - 1
        for _ in range(requests):
            await asyncio.sleep(time_pause)
            if self.requests:
                await self.get_request(new=False).approve(bot)
            else:
                self._stop_job()
                break


class Admin:
    db = DataBase()
    _admins = {}

    def __new__(cls, admin_tg_id: int):
        if admin_tg_id not in cls._admins:
            print('Создал пользователя')
            _instance = super().__new__(cls)
            _instance.admin_tg_id = admin_tg_id
            cls._admins[admin_tg_id] = _instance
        return cls._admins[admin_tg_id]

    # def __init__(self, admin_tg_id: int):
    #     print('Создал пользователя')
    #     self.admin_tg_id = admin_tg_id
    #     # self._channels = None

    @property
    def channels(self):
        # if self._channels is None:
        return {int(channel_tg_id[0]): Channel(channel_tg_id[0], self.admin_tg_id)
                for channel_tg_id in self.db.load_channels(self.admin_tg_id)}
        # return self._channels


class Limits:
    def __init__(self, admin_tg_id: int, channel_tg_id: int):
        limits = DataBase().get_admin_limits(admin_tg_id, channel_tg_id)
        self.min = limits[0]
        self.max = limits[1]
