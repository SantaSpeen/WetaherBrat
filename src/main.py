from pathlib import Path

import telebot
from loguru import logger

from models import db_connect, get_user
from config import Config

logger.info("Starting WetaherBrat...")
file = Path("config.yml")
config = Config(file)
db_connect(config.database)

bot = telebot.TeleBot(config.token, parse_mode="MARKDOWN")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(message)
    user, new = get_user(message.from_user)
    if new:
        bot.reply_to(message, f"Привет, {message.from_user.first_name}. Твой ID: {user.id}\n"
                     "Давай настроем бота для тебя (используй клавиатуру)")
    else:
        bot.reply_to(message, f"Привет, снова?")


if __name__ == '__main__':
    try:
        info = bot.get_me()
        logger.info(f"Bot: {info.first_name}(@{info.username}; id{info.id})")
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 401:
            logger.error("Bad token.")
        else:
            raise e
        exit(1)
    logger.success("WetaherBrat started.")
    bot.infinity_polling()
