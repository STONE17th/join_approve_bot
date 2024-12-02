from aiogram import Bot

import asyncio
from dataclasses import dataclass
from datetime import datetime
from random import randint

from database.data_base import DataBase


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

    def __init__(self, channel_tg_id: int, request_tg_id: int, creation_date: datetime):
        self.channel_tg_id = channel_tg_id
        self.request_tg_id = request_tg_id
        self.creation_date = creation_date

    @classmethod
    def create(cls, channel_tg_id: int, request_tg_id: int):
        creation_date = datetime.now()
        DataBase.add_request(channel_tg_id, request_tg_id, creation_date)

    async def approve(self, bot: Bot):
        # approve_date = datetime.now()
        DataBase.delete_request(self.channel_tg_id, self.request_tg_id)
        try:
            await bot.approve_chat_join_request(
                chat_id=self.channel_tg_id,
                user_id=self.request_tg_id,
            )
            return True
        except Exception as e:
            return False


class Channel:
    tasks = {}

    def __init__(self, admin_tg_id: int, channel_tg_id: int, channel_title: str, min_requests: int, max_requests: int):
        self.admin_tg_id = admin_tg_id
        self.channel_tg_id = channel_tg_id
        self.title = channel_title
        self.limit = Limits(min=min_requests, max=max_requests)
        self._requests: list[Request] | None = None

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
        return self._requests

    def set_limits(self, values: tuple[int, int]):
        DataBase.set_admin_limits(self.admin_tg_id, self.channel_tg_id, *values)

    def get_request(self, new: bool) -> Request:
        if self.requests:
            return self.requests.pop() if new else self.requests.pop(0)

    @property
    def check_auto(self) -> bool:
        return self.channel_tg_id in Channel.tasks

    async def start_auto_approve(self, time_delta: tuple[int, int], bot: Bot):
        self.limit.min, self.limit.max = time_delta
        task = asyncio.create_task(self._auto_approve(bot))
        Channel.tasks[self.channel_tg_id] = task

    def stop_auto_approve(self):
        if self.check_auto:
            self._stop_job()

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


class Admin:
    db = DataBase()

    def __init__(self, admin_tg_id: int):
        self.admin_tg_id = admin_tg_id
        self._channels = None

    @property
    def channels(self):
        if self._channels is None:
            self._channels = {channel[1]: Channel(*channel) for channel in self.db.get_channels(self.admin_tg_id)}
        return self._channels
