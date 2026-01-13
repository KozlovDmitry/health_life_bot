import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    # WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
    TELEGRAM_BOT_TOKEN = "8556699634:AAGbYa1rKh-8XsKQLMagT1I9hJxBZZd7peI"
    WEATHER_TOKEN = "23e4cb20d027f986ae78f2d7304ebc5f"


config = Config()
