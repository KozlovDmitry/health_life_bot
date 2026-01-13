import logging

from aiogram import Router, types
from aiogram.filters.command import Command

from utils.cache import CACHE

logger = logging.getLogger(__package__)

check_progress_router = Router()


@check_progress_router.message(Command("check_progress"))
async def check_progress(message: types.Message):
    logger.info(f"Get message {message.text}")

    user_info = CACHE[message.from_user.id]

    current_water = user_info.get("current_water", 0)
    target_water = user_info.get("target_water")

    current_calories = user_info.get("current_calories", 0)
    target_calories = user_info.get("target_calories")
    burned_calories = user_info.get("burned_calories", 0)

    current_temp = user_info["current_temp"]

    message_text = (
        f"Прогресс:\n"
        f"\t- Выпито: {current_water} мл из {target_water} мл.\n"
        f"\t- Осталось: {target_water - current_water if current_water < target_water else 0} мл.\n\n"
        f"Калории:\n"
        f"\t- Потреблено: {current_calories} ккал из {target_calories} ккал.\n"
        f"\t- Сожжено: {burned_calories} ккал.\n"
        f"\t- Баланс: {target_calories + current_calories - burned_calories} ккал.\n\n"
        f"Доп. информация:\n"
        f"\t- Город: {user_info['city']}\n"
        f"\t- Температура в городе: {f'{current_temp} To refresh - press /refresh_current_temp' if current_temp is not None else 'Trying to get temp in your city... To refresh - press /refresh_current_temp'}\n"
    )

    await message.answer(message_text)
