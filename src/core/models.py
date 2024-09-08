from loguru import logger
from peewee import SqliteDatabase, Model, IntegerField, CharField, DoesNotExist


class Users(Model):
    id = IntegerField(null=True, primary_key=True)
    user_id = IntegerField()
    lang = CharField(3)
    state = IntegerField(default=0)
    city = CharField(null=True)
    timezone = IntegerField(default=10800)
    alarm_time = CharField(10, null=True, default="8:00")

    class Meta:
        table_name = 'users'


def db_connect(config):
    match config.type:
        case "SQLITE":
            db = SqliteDatabase(config.file)
        case _:
            logger.error("SQLITE only.. NOW")
            exit(0)

    Users._meta.database = db
    db.connect()
    db.create_tables([Users])
    logger.success("Database loaded.")


def get_user(from_user):
    user_id = from_user.id
    new = False
    try:
        user = Users().get(Users.user_id == user_id)
    except DoesNotExist:
        user = Users(user_id=user_id, lang=from_user.language_code)
        user.save()
        logger.info(f"[users] New user: tg-id: {user_id}; id: {user.id}")
        new = True
    return user, new
