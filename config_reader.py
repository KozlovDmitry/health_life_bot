import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")


config = Config()
