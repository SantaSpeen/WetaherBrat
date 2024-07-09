import telebot
from ruamel.yaml import YAML

from models import Users, DoesNotExist

yaml = YAML()
token = ""
bot = telebot.TeleBot(token, parse_mode="MARKDOWN")


def get_user(user_id):
    new = False
    try:
        user = Users().get(Users.user_id == user_id)
    except DoesNotExist:
        user = Users(user_id=user_id)
        user.save()
        new = True
    return user, new


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user, new = get_user(message.from_user.id)
    if new:
        bot.reply_to(message,
                     f"Привет, {message.from_user.first_name}. Твой ID: {user.id}\n"
                     "Давай настроем бота для тебя (используй клавиатуру)")
    else:
        bot.reply_to(message, f"Привет, снова?")


bot.infinity_polling()
