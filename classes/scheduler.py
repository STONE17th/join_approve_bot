from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot_scheduler = AsyncIOScheduler()


class Scheduler:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = AsyncIOScheduler()
        return cls.instance
