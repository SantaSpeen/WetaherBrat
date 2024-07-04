import telebot
from ruamel.yaml import YAML

from models import Users

yaml = YAML()

bot = telebot.TeleBot("TOKEN", parse_mode="MARKDOWN")



bot.infinity_polling()
