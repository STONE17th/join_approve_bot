from aiogram import Bot

from database.data_base import DataBase


class Request:

    def __init__(self, channel_tg_id: int, request_tg_id: int):
        self.channel_tg_id = channel_tg_id
        self.request_tg_id = request_tg_id

    async def approve(self, db: DataBase, bot: Bot):
        db.delete_request(self.channel_tg_id, self.request_tg_id)
        try:
            await bot.approve_chat_join_request(
                chat_id=self.channel_tg_id,
                user_id=self.request_tg_id,
            )
            return True
        except Exception as e:
            print(f'Не удалось добавить {self.request_tg_id}')
            return False


class Channel:
    db = DataBase()

    def __init__(self, channel_tg_id: int, admin_tg_id: int):
        self.channel_tg_id = channel_tg_id
        self.admin_tg_id = admin_tg_id
        self._requests = None

    @property
    def requests(self):
        if self._requests is None:
            self._requests = [Request(self.channel_tg_id, request_tg_id)
                              for request_tg_id in self.db.load_requests(self.channel_tg_id)]
        return self._requests

    async def title(self, bot: Bot):
        channel = await bot.get_chat(self.channel_tg_id)
        return channel.title

    def get_request(self, new: bool):
        if self._requests:
            return self._requests.pop(0) if new else self._requests.pop()


class Admin:
    db = DataBase()

    def __init__(self, admin_tg_id: int):
        self.admin_tg_id = admin_tg_id
        self._channels = None

    @property
    def channels(self):
        if self._channels is None:
            self._channels = [Channel(channel_tg_id[0], self.admin_tg_id)
                              for channel_tg_id in self.db.load_channels(self.admin_tg_id)]
        return self._channels
