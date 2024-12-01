from aiogram import Router

from .callbacks import router as callbacks_router
from .commands import commands_router

main_router = Router()
main_router.include_routers(
    commands_router,
    callbacks_router,
)

__all__ = [
    'main_router',
]
