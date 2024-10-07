from aiogram import Bot

from database.data_base import DataBase


class Channel:
    db = DataBase()

    def __init__(self, admin_tg_id: int, channel_id: int, channel_tg_id: int):
        self.id = channel_id
        self.tg_id = channel_tg_id
        self.admin = admin_tg_id
        self.requests = self._requests()

    @classmethod
    def new(cls, admin_tg_id: int, tg_id: int):
        cls.db.add_new_channel(admin_tg_id, tg_id)
        return cls.load(tg_id)

    @classmethod
    def load(cls, tg_id: int):
        channel_id, admin_tg_id = cls.db.load_channel(tg_id)
        return cls(admin_tg_id, channel_id, tg_id)

    def _requests(self):
        return [Request(channel[1], self.id, self.tg_id) for channel in sorted(Channel.db.load_requests(self.id))]

    async def title(self, bot: Bot):
        channel = await bot.get_chat(self.tg_id)
        return channel.title

    async def approve_request(self, bot: Bot, new: bool):
        if self.requests:
            request = self.requests.pop(0) if new else self.requests.pop()
            await request.approve(self.db, bot)
            return True

    async def amount_requests_in_channel(self, bot: Bot, full: bool = True):
        if full:
            return f'{await self.title(bot)}: {len(self.requests)}'
        return f'{len(self.requests)}'

    def __str__(self):
        return f'ID: {self.id} ({self.tg_id})'


class Request:

    def __init__(self, tg_id: int, channel_id: int, channel_tg_id: int):
        self.tg_id = tg_id
        self.channel_tg_id = channel_tg_id
        self.channel_id = channel_id

    async def approve(self, db: DataBase, bot: Bot):
        db.delete_join_request(self.channel_id, self.tg_id)
        try:
            await bot.approve_chat_join_request(self.channel_tg_id, self.tg_id)
            return True
        except:
            print(f'Не удалось добавить {self.tg_id}')
            return False


class Admin:
    db = DataBase()

    def __init__(self, tg_id: int):
        self.tg_id = tg_id

    @property
    def channels(self):
        return {channel[1]: Channel(self.tg_id, *channel) for channel in self.db.load_channels(self.tg_id)}

    async def amount_requests_in_channels(self, bot: Bot):
        result = []
        for channel in self.channels.values():
            result.append(await channel.amount_requests_in_channel(bot))
        return '\n' + '\n'.join(result)
