from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot_scheduler = AsyncIOScheduler()


class Scheduler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = AsyncIOScheduler()
        return cls._instance
