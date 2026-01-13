import logging
import aiohttp

from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from utils.cache import CACHE, PRODUCT_CACHE

logger = logging.getLogger(__package__)

log_food_router = Router()


class Food(StatesGroup):
    name = State()
    calories_100g = State()
    weight = State()


async def get_product_info(product_name):
    # Cache known products
    if product_name not in PRODUCT_CACHE:

        url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info(f"Product API req successful")
                    try:
                        response_json = await response.json()
                        products = response_json.get("products")
                        if not products:
                            return

                        first_product = products[0]
                        PRODUCT_CACHE[product_name] = {
                            "product_name": first_product.get(
                                "product_name", "Unknown"
                            ),
                            "product_calories": (
                                first_product.get("nutriments") or {}
                            ).get("energy-kcal_100g", 0),
                        }

                    except Exception as e:
                        logger.warning(
                            f"Parsing product API req unsuccessful. Error: {e}"
                        )
                else:
                    logger.warning(
                        f"Product API req unsuccessful. Status_code: {response.status}"
                    )

    return PRODUCT_CACHE.get(product_name)


@log_food_router.message(Command("log_food"))
async def log_food(message: types.Message, command: CommandObject, state: FSMContext):
    logger.info(f"Get message {message.text}")
    if message.from_user.id not in CACHE:
        await message.answer(f"Сначала воспользуйтесь командой /set_profile")
        return

    if not command.args:
        await message.answer(f"Укажите название продукта")
        return

    await state.set_state(Food.name)
    product_name = "".join(command.args)
    await state.update_data(name=product_name)

    product_info = await get_product_info(product_name)
    if not product_info:
        await state.clear()
        await message.answer(f"Калорийность данного продукта не найдена")
    else:
        await message.answer(
            f"{product_info['product_name']} — {product_info['product_calories']} ккал на 100 г. Сколько грамм вы съели?"
        )
        await state.update_data(calories_100g=product_info.get("product_calories"))
        await state.set_state(Food.weight)


@log_food_router.message(Food.weight)
async def process_food_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)
        calories_100g = (await state.get_data()).get("calories_100g", 0)
        current_calories = round(0.01 * calories_100g * weight, 1)

        CACHE[message.from_user.id]["current_calories"] += current_calories
        CACHE[message.from_user.id]["log_calories"].append(
            {
                "time": datetime.now(),
                "value": current_calories,
            }
        )

        await message.answer(f"Записано: {current_calories}")
    except Exception:
        await message.reply("Некорректное значение")
        return

    await state.clear()
