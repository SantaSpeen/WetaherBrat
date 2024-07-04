from peewee import SqliteDatabase, Model, IntegerField, CharField

class BasicModel(Model):
    class Meta:
        database = SqliteDatabase('base.db')


class Users(BasicModel):

    id = IntegerField(null=True, primary_key=True)
    user_id = IntegerField()
    city = CharField(null=True)
    timezone = IntegerField(default=3)
    alarm_time = CharField(10)

    class Meta:
        table_name = 'users'  

