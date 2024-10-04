from aiogram import Bot

from database.data_base import DataBase


class Channel:
    db = DataBase()

    def __init__(self, admin_tg_id: int, channel_id: int, channel_tg_id: int, bot: Bot):
        self.id = channel_id
        self.tg_id = channel_tg_id
        self.admin = admin_tg_id
        self.bot = bot

    @classmethod
    def new(cls, admin_tg_id: int, tg_id: int, bot: Bot):
        cls.db.add_new_channel(admin_tg_id, tg_id)
        return cls.load(tg_id, bot)

    @classmethod
    def load(cls, tg_id: int, bot: Bot):
        channel_id, admin_tg_id = cls.db.load_channel(tg_id)
        return cls(admin_tg_id, channel_id, tg_id, bot)

    @property
    def requests(self):
        return list(map(lambda x: x[1], sorted(Channel.db.load_channel_requests(self.id))))

    async def title(self):
        channel = await self.bot.get_chat(self.tg_id)
        return channel.title

    async def amount_requests(self, string: bool = True):
        if string:
            return f'{await self.title()}: {len(self.requests)}'
        return await self.title(), self.requests

    def __str__(self):
        return f'ID: {self.id} ({self.tg_id})'


class User:
    db = DataBase()

    def __init__(self, tg_id: int, bot: Bot):
        self.id = tg_id
        self.bot = bot


class Admin(User):
    def __init__(self, tg_id: int, bot: Bot):
        super().__init__(tg_id, bot)

    @property
    async def channels(self):
        return list(map(lambda x: Channel.load(x[0], self.bot), User.db.load_admin_channels(self.id)))

    @property
    async def requests_in_channels(self):
        result = []
        for channel in await self.channels:
            data = await channel.amount_requests()
            result.append(data)
        return '\n'.join(result)
    #
    # async def for_keyboard(self):
    #     return [(await channel.amount_requests(string=False)) for channel in self.channels]


class Request:
    pass
