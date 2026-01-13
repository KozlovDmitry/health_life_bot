import asyncio
import logging

from aiogram import Dispatcher, Bot

from config_reader import config
from handlers import (
    set_profile_router,
    log_water_router,
    log_workout_router,
    check_progress_router,
    log_food_router,
    check_progress_graph_router,
    health_router,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__package__)

bot = Bot(token=config.telegram_bot_token.get_secret_value())
dp = Dispatcher()

dp.include_router(set_profile_router)
dp.include_router(log_water_router)
dp.include_router(log_workout_router)
dp.include_router(check_progress_router)
dp.include_router(log_food_router)
dp.include_router(check_progress_graph_router)
dp.include_router(health_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
