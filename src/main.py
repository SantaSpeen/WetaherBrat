import datetime
import time
from pathlib import Path
from threading import Thread

import requests
import telebot
from loguru import logger

from core.models import db_connect, get_user, Users
from core.config import Config
from core.i18n import I18N

logger.info("Starting WetaherBrat...")
file = Path("config.yml")
config = Config(file)
db_connect(config.database)
i18n = I18N(config.i18n)

bot = telebot.TeleBot(config.token, parse_mode="MARKDOWN")

def get_weather(city, lang):
    try:
        return requests.get(f"https://api.openweathermap.org/data/2.5/weather?"
                            f"q={city}&lang={lang}&appid={config.weather.token}&units=metric").json()
    except Exception as e:
        logger.exception(e)
        return {}

def get_user_weather(city, lang):
    weather = get_weather(city, lang)
    if not weather:
        return "error"
    if weather["cod"] == '404':
        return None
    else:
        data = {
            "city": city,
            "temp": weather["main"]["temp"],
            "feel_temp": weather["main"]["feels_like"],
            "desc": weather["weather"][0]["description"],
            "wind": weather["wind"]["speed"],
            "_tz": weather["timezone"]
        }
        return data

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user, new = get_user(message.from_user)
    if new:
        bot.reply_to(message, i18n.get("start", user, name=message.from_user.first_name))
        bot.send_message(message.chat.id, i18n.get("request_city", user))
    else:
        bot.reply_to(message, i18n.get("start_again", user))


@bot.message_handler(content_types=['text'])
def global_parser(message):
    user, _ = get_user(message.from_user)
    match user.state:
        case 0:
            city = message.text.strip()
            weather = get_user_weather(city, user.lang)
            if not weather:
                bot.reply_to(message, i18n.get("not_found_city", user))
            else:
                bot.reply_to(message, i18n.get("saved_city", user))
                user.timezone = weather["_tz"]
                user.state = 1
                user.city = city
                bot.send_message(message.from_user.id, i18n.get("report_weather", user, **weather))
                user.save()
        case 1:
            match message.text.lower()[1:]:
                case "help":
                    bot.send_message(message.from_user.id, i18n.get("help", user))
                case "w":
                    weather = get_user_weather(user.city, user.lang)
                    bot.send_message(message.from_user.id, i18n.get("report_weather", user, **weather))
                case "settime":
                    user.state = 2
                    user.save()
                    bot.send_message(message.from_user.id, i18n.get("request_time", user))
                case "setcity":
                    user.state = 3
                    user.save()
                    bot.send_message(message.from_user.id, i18n.get("request_time", user))
                case "settz":
                    user.state = 4
                    user.save()
                    bot.send_message(message.from_user.id, i18n.get("request_timezone", user))
                case _:
                    bot.reply_to(message, i18n.get("not_found_command", user))
        case 2:
            try:
                t = message.text.strip()
                time.strptime(t, '%H:%M')
                user.alarm_time = t
                bot.reply_to(message, i18n.get("ready", user))
            except ValueError:
                bot.reply_to(message, i18n.get("error", user))
            user.state = 1
            user.save()
        case 3:
            city = message.text.strip()
            weather = get_user_weather(city, user.lang)
            if not weather:
                bot.reply_to(message, i18n.get("not_found_city", user))
            else:
                bot.reply_to(message, i18n.get("saved_city", user))
                user.state = 1
                user.city = city
                user.save()
        case 4:
            bot.send_message(message.from_user.id, "WIP")
            user.state = 1
            user.save()


def auto_sender():
    while True:
        users = Users.select().where(Users.state == 1)
        for user in users:
            tz = datetime.timezone(datetime.timedelta(seconds=user.timezone))
            td = datetime.datetime.now(tz)
            if td.strftime("%H:%M") == user.alarm_time:
                logger.info(f"[auto_sender] Send weather to user: tg-id: {user.user_id}; city: {user.city!r} at {user.alarm_time!r}")
                weather = get_user_weather(user.city, user.lang)
                if weather:
                    bot.send_message(user.user_id, i18n.get("report_weather", user, **weather))
        time.sleep(60)

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
    t1 = Thread(target=auto_sender)
    t1.start()
    bot.infinity_polling()
