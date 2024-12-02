import asyncio

from aiogram import Bot
from apscheduler.triggers.interval import IntervalTrigger

import asyncio
from asyncio import create_task, run, sleep
from dataclasses import dataclass
from datetime import datetime
from random import randint

from classes.scheduler import Scheduler
from database.data_base import DataBase


# async def print_something(seconds: int):
#     while True:
#         await sleep(seconds)
#         print(f'тут {seconds}')


# async def main():
#     task1 = create_task(thread_maintaining_communication(3), name='123')
#     task2 = create_task(thread_maintaining_communication(5), name='fffff')
#     print(asyncio.get_running_loop().is_running())
#     for task in asyncio.all_tasks():
#         print(task.get_name())
#     while True:
#         print('Сплю 10 сек')
#         await sleep(10)
#         task2.cancel()
#         await sleep(10)
#         task1.cancel()
#
#
# run(main())


@dataclass
class Limits:
    min: int = 0
    max: int = 0

    @classmethod
    def load(cls, admin_tg_id, channel_tg_id):
        min_value, max_value = DataBase().get_admin_limits(admin_tg_id, channel_tg_id)
        return cls(min_value, max_value)

    def save(self, admin_tg_id, channel_tg_id):
        DataBase().set_admin_limits(
            admin_tg_id=admin_tg_id,
            channel_tg_id=channel_tg_id,
            min_value=self.min,
            max_value=self.max,
        )


class Request:
    # _db = DataBase()

    def __init__(self, channel_tg_id: int, request_tg_id: int, creation_date: datetime):
        self.channel_tg_id = channel_tg_id
        self.request_tg_id = request_tg_id
        self.creation_date = creation_date

    @classmethod
    def create(cls, channel_tg_id: int, request_tg_id: int):
        creation_date = datetime.now()
        DataBase.add_request(channel_tg_id, request_tg_id, creation_date)

    async def approve(self, bot: Bot):
        approve_date = datetime.now()
        DataBase.delete_request(self.channel_tg_id, self.request_tg_id)
        try:
            print(f'Пробую принять {self.channel_tg_id} - {self.request_tg_id}')
            await bot.approve_chat_join_request(
                chat_id=self.channel_tg_id,
                user_id=self.request_tg_id,
            )
            # print('Пробую удалить')
            # DataBase.approve_request(
            #     channel_tg_id=self.channel_tg_id,
            #     request_tg_id=self.request_tg_id,
            #     approve_date=approve_date,
            # )
            print(f'Принял {self.channel_tg_id} - {self.request_tg_id}')
            return True
        except Exception as e:
            print(e)
            print(f'Не принял {self.channel_tg_id} - {self.request_tg_id}')
            return False

    # def __eq__(self, other):
    #     return self.request_tg_id == other.request_tg_id
    #
    # def __str__(self):
    #     # return f'{self.request_tg_id:>15} {self.creation_date:<15}'
    #     return f'{self.request_tg_id}'

    # def test(self):
    #     # print(self.request_tg_id)
    #     Request._db.delete_request(self.channel_tg_id, self.request_tg_id)


class Channel:
    # db = DataBase()
    _bot_scheduler = Scheduler()
    tasks = {}

    # def __new__(cls, *args, **kwargs):
    #     if Channel._bot_scheduler is None:
    #         Channel._bot_scheduler = AsyncIOScheduler()

    def __init__(self, admin_tg_id: int, channel_tg_id: int, channel_title: str, min_requests: int, max_requests: int):
        self.admin_tg_id = admin_tg_id
        self.channel_tg_id = channel_tg_id
        self.title = channel_title
        self.limit = Limits(min=min_requests, max=max_requests)
        self._requests: list[Request] | None = None

    # @staticmethod
    # async def say_something(text, seconds):
    #     while True:
    #         print(f'{text} ин {seconds}')
    #         await asyncio.sleep(seconds)
    #
    # @classmethod
    # async def start_task(cls, task_id, time):
    #     task = asyncio.create_task(cls.say_something(f'{task_id}', time))
    #     cls.tasks[task_id] = task
    #     print(cls.tasks)
    #
    # @classmethod
    # async def stop_task(cls, task_id):
    #     print(cls.tasks)
    #     task = cls.tasks[task_id]
    #     print(type(task))
    #     task.cancel()

    @classmethod
    def by_tg_id(cls, admin_tg_id: int, channel_tg_id: int):
        response = DataBase.get_channel(admin_tg_id, channel_tg_id)
        return cls(*response)

    @property
    def requests(self) -> list[Request]:
        if self._requests is None:
            request_list = [Request(self.channel_tg_id, *request) for request in
                            DataBase.load_requests(self.channel_tg_id)]
            self._requests = sorted(request_list, key=lambda x: x.creation_date)
            # self._requests = request_list
        return self._requests

    def set_limits(self, values: tuple[int, int]):
        DataBase.set_admin_limits(self.admin_tg_id, self.channel_tg_id, *values)

    # async def title(self, bot: Bot):
    #     channel = await bot.get_chat(self.channel_tg_id)
    #     return channel.title

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
        return self.channel_tg_id in Channel.tasks

    async def start_auto_approve(self, time_delta: tuple[int, int], bot: Bot):
        self.limit.min, self.limit.max = time_delta
        task = asyncio.create_task(self._auto_approve(bot))
        Channel.tasks[self.channel_tg_id] = task
        # self._bot_scheduler.add_job(
        #     func=await self.auto_approve(bot),
        #     args=(bot,),
        #     id=f'{self.channel_tg_id}',
        #     trigger=IntervalTrigger(minutes=60),
        #     replace_existing=True,
        # )
        # if not self._bot_scheduler.running:
        #     self._bot_scheduler.start()

    def stop_auto_approve(self):
        if self.check_auto:
            print('Прием заявок отключен')
            self._stop_job()
        print(Channel.tasks)
        # if not self._bot_scheduler.get_jobs():
        #     self._bot_scheduler.shutdown()

    async def _auto_approve(self, bot: Bot):
        while True:
            requests_per_hour = randint(self.limit.min, self.limit.max)
            time_pause = 3600 // requests_per_hour
            for _ in range(requests_per_hour):
                if self.requests:
                    await self.get_request(new=False).approve(bot)
                else:
                    self._stop_job()
                    break
                await asyncio.sleep(time_pause)

    def _stop_job(self):
        task = Channel.tasks.pop(self.channel_tg_id)
        task.cancel()
        # self._bot_scheduler.remove_job(job_id=f'{self.channel_tg_id}')
        # self.min_requests, self.max_requests = 0, 0


class Admin:
    db = DataBase()

    # _admins = {}

    # def __new__(cls, admin_tg_id: int):
    #     if admin_tg_id not in cls._admins:
    #         print('Создал пользователя')
    #         _instance = super().__new__(cls)
    #         _instance.admin_tg_id = admin_tg_id
    #         cls._admins[admin_tg_id] = _instance
    #     return cls._admins[admin_tg_id]

    def __init__(self, admin_tg_id: int):
        self.admin_tg_id = admin_tg_id
        self._channels = None

    @property
    def channels(self):
        if self._channels is None:
            # return [channel_tg_id[0] for channel_tg_id in self.db.load_channels(self.admin_tg_id)]
            self._channels = {channel[1]: Channel(*channel) for channel in self.db.get_channels(self.admin_tg_id)}
        return self._channels
