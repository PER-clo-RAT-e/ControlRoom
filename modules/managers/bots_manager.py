from modules.managers.bots.discord_bot import DiscordBot
from modules.managers.bots.telegram_bot import TelegramBot

from dotenv import load_dotenv
import os

class BotManager():
    def __init__(self) -> None:
        load_dotenv()
        self.discord = DiscordBot(os.getenv('DISCORD_BOT_TOKEN'))
        self.discord = TelegramBot(os.getenv('TELEGRAM_BOT_TOKEN'))