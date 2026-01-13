import logging

from aiogram import Router, types
from aiogram.filters.command import Command

logger = logging.getLogger(__package__)

health_router = Router()


@health_router.message(Command("health"))
async def set_profile(message: types.Message):
    logger.info(f"Get message {message.text}")

    await message.answer("ok")
