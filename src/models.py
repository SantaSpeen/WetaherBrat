from peewee import SqliteDatabase, Model, IntegerField, CharField, DoesNotExist

db = SqliteDatabase('base.db')

class Users(Model):

    id = IntegerField(null=True, primary_key=True)
    user_id = IntegerField()
    city = CharField(null=True)
    timezone = IntegerField(default=3)
    alarm_time = CharField(10, null=True)

    class Meta:
        table_name = 'users'
        database = db

db.connect()
db.create_tables([Users])
