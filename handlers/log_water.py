import logging

from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject

from utils.cache import CACHE
from utils.common_func import get_float_safe

logger = logging.getLogger(__package__)

log_water_router = Router()


@log_water_router.message(Command("log_water"))
async def log_water(message: types.Message, command: CommandObject):
    logger.info(f"Get message {message.text}")
    if message.from_user.id not in CACHE:
        await message.answer(f"Сначала воспользуйтесь командой /set_profile")
        return

    if not command.args:
        await message.answer(f"Укажите в мл количество выпитой воды")
    else:
        water_volume = get_float_safe("".join(command.args))

        if not water_volume:
            await message.answer(f"Некорректный формат ввода")

        else:
            CACHE[message.from_user.id]["current_water"] += water_volume
            CACHE[message.from_user.id]["log_water"].append(
                {
                    "time": datetime.now(),
                    "value": water_volume,
                }
            )

            if (
                CACHE[message.from_user.id]["current_water"]
                >= CACHE[message.from_user.id]["target_water"]
            ):
                msg = "Норма воды на сегодня выпита"
            else:
                msg = f"До выполнения нормы осталось {CACHE[message.from_user.id]['target_water'] - CACHE[message.from_user.id]['current_water']} мл."

            await message.answer(msg)
