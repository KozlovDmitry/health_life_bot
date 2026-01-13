import logging
import io

import matplotlib.pyplot as plt

from datetime import datetime

from aiogram import Router, types
from aiogram.filters.command import Command
from utils.cache import CACHE

logger = logging.getLogger(__package__)

check_progress_graph_router = Router()


async def create_graph(message: types.Message):
    water_graph = CACHE[message.from_user.id]["log_water"]
    calories_graph = CACHE[message.from_user.id]["log_calories"]
    graph_name_to_data = {
        "Прогресс по воде": {"data": water_graph, "unit": "мл"},
        "Прогресс по калориям": {"data": calories_graph, "unit": "ккал"},
    }

    fig, axes = plt.subplots(
        len(graph_name_to_data), 1, figsize=(len(graph_name_to_data) * 6, 8)
    )
    for index, (grap_name, graph_datas) in enumerate(graph_name_to_data.items()):
        graph_data = graph_datas["data"]
        unit = graph_datas["unit"]

        axes[index].plot(
            [point["time"] for point in graph_data],
            [point["value"] for point in graph_data],
        )
        axes[index].set_xlabel("Время")
        axes[index].set_xlabel(unit)
        axes[index].set_title(grap_name)
        axes[index].grid(True)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close()

    image_bytes = buf.getvalue()
    buf.close()

    return types.BufferedInputFile(image_bytes, filename=f"graph_{datetime.now()}.png")


@check_progress_graph_router.message(Command("check_progress_graph"))
async def check_progress_graph(message: types.Message):
    logger.info(f"Get message {message.text}")
    if message.from_user.id not in CACHE:
        await message.answer(f"Сначала воспользуйтесь командой /set_profile")
        return

    image = await create_graph(message)
    await message.answer_photo(image)
