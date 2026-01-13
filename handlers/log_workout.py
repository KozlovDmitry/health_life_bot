import logging

from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject

from utils.cache import CACHE
from utils.common_func import get_float_safe

logger = logging.getLogger(__package__)

log_workout_router = Router()


def get_workout_and_time_session_safe(value) -> tuple[str | None, float | None]:
    try:
        workout_type, time_session = value.split()
        return workout_type, get_float_safe(time_session)
    except Exception:
        logger.warning(f"Couldn't convert value {value}(get_workout_and_time_session)")
        return None, None


@log_workout_router.message(Command("log_workout"))
async def log_workout(message: types.Message, command: CommandObject):
    logger.info(f"Get message {message.text}")
    if message.from_user.id not in CACHE:
        await message.answer(f"Сначала воспользуйтесь командой /set_profile")
        return

    if not command.args:
        await message.answer(f"Укажите вид тренироки и длитеьность в минутах")
    else:
        workout_type, time_session = get_workout_and_time_session_safe(
            "".join(command.args)
        )

        if not workout_type or not time_session:
            await message.answer(f"Некорректный формат ввода")

        else:
            workout_calories_coef = 10
            burned_calories = time_session * workout_calories_coef

            workout_water_coef = 6
            additional_water = time_session * workout_water_coef

            CACHE[message.from_user.id]["target_water"] += additional_water
            CACHE[message.from_user.id]["burned_calories"] += burned_calories
            CACHE[message.from_user.id]["log_calories"].append(
                {
                    "time": datetime.now(),
                    "value": -burned_calories,
                }
            )

            msg = f"{workout_type} {time_session} минут — {burned_calories} ккал. Дополнительно: выпейте {additional_water} мл воды."
            await message.answer(msg)
