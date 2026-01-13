import logging
import aiohttp

from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.cache import CACHE
from config_reader import config

logger = logging.getLogger(__package__)

set_profile_router = Router()


@set_profile_router.message(Command("set_profile"))
async def set_profile(message: types.Message, state: FSMContext):
    logger.info(f"Get message {message.text}")

    await process_set_profile(message, state)


class User(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity_level = State()
    city = State()

    target_calories = State()


async def process_set_profile(message: types.Message, state: FSMContext):
    logger.info(f"Get message {message.text}")

    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(User.weight)


@set_profile_router.message(User.weight)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        CACHE[message.from_user.id]["weight"] = weight

        await state.update_data(weight=weight)
        await message.reply("Введите ваш рост (в см):")
        await state.set_state(User.height)

    except Exception:
        await message.reply("Некорректное значение")


@set_profile_router.message(User.height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        CACHE[message.from_user.id]["height"] = height

        await state.update_data(height=height)
        await message.reply("Введите ваш возраст:")
        await state.set_state(User.age)

    except Exception:
        await message.reply("Некорректное значение")


@set_profile_router.message(User.age)
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        CACHE[message.from_user.id]["age"] = age

        await state.update_data(age=age)
        await message.reply("Сколько минут активности у вас в день?")
        await state.set_state(User.activity_level)

    except Exception:
        await message.reply("Некорректное значение")


@set_profile_router.message(User.activity_level)
async def process_activity_level(message: types.Message, state: FSMContext):
    try:
        activity_level = float(message.text)
        CACHE[message.from_user.id]["activity_level"] = activity_level

        await state.update_data(activity_level=activity_level)
        await message.reply("В каком городе вы находитесь?")
        await state.set_state(User.city)

    except Exception:
        await message.reply("Некорректное значение")


@set_profile_router.message(User.city)
async def process_city(message: types.Message, state: FSMContext):
    CACHE[message.from_user.id]["city"] = message.text
    CACHE[message.from_user.id]["target_calories"] = await get_target_calories(
        message.from_user.id
    )

    await message.answer(
        f"Ваши данные сохранены. {CACHE[message.from_user.id]}. Для отображения прогресса используйте /check_progress"
    )

    CACHE[message.from_user.id]["target_water"] = await get_target_water(
        message.from_user.id
    )

    await state.clear()


async def get_target_water(user_id):
    temp = await get_current_temp(user_id)

    temp_threshold = 25
    additional_water = 0
    if temp is not None and temp > temp_threshold:
        additional_water = 500

    return int(
        30 * CACHE[user_id]["weight"]
        + 500 / CACHE[user_id]["activity_level"]
        + additional_water
    )


async def get_current_temp(user_id):
    city = CACHE[user_id]["city"]
    token = config.weather_token.get_secret_value()

    if not city or not token:
        return

    params = {"q": city, "appid": token}
    url = "http://api.openweathermap.org/data/2.5/weather"

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                logger.info(f"Weather API req successful. User: {user_id}")
                try:
                    response_json = await response.json()
                    CACHE[user_id]["current_temp"] = round(
                        (response_json.get("main") or {}).get("temp") - 273, 1
                    )

                    return CACHE[user_id]["current_temp"]

                except Exception as e:
                    logger.warning(
                        f"Parsing weather API req unsuccessful. User: {user_id}. Error: {e}"
                    )
            else:
                logger.warning(
                    f"Weather API req unsuccessful. User: {user_id}, status_code: {response.status}"
                )

    return


async def get_target_calories(user_id):
    return int(
        10 * CACHE[user_id]["weight"]
        + 6.25 * CACHE[user_id]["height"]
        - 5 * CACHE[user_id]["age"]
        + (CACHE[user_id]["activity_level"] * 3)
    )


@set_profile_router.message(Command("refresh_current_temp"))
async def refresh_current_temp(message: types.Message):
    logger.info(f"Get message {message.text}")
    await message.answer("Updating...")

    temp = await get_current_temp(message.from_user.id)
    if temp is not None:
        await message.answer("Temp updated")
    else:
        await message.answer("Couldn't update temp")
