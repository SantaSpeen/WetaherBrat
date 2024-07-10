from pathlib import Path
import telebot
from loguru import logger

from core.models import db_connect, get_user
from core.config import Config
from core.i18n import I18N

logger.info("Starting WetaherBrat...")
file = Path("config.yml")
config = Config(file)
db_connect(config.database)
i18n = I18N(config.i18n)

bot = telebot.TeleBot(config.token, parse_mode="MARKDOWN")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user, new = get_user(message.from_user)
    if new:
        bot.reply_to(message, i18n.get("start", user, message))
    else:
        bot.reply_to(message, i18n.get("start_again", user, message))


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
