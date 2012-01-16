import datetime
from google.appengine.ext import db

DAY_LOG_DAILY = 0
DAY_LOG_RETRO = 1

class Retro(db.Model):
    goal = db.TextProperty()
    good = db.TextProperty()
    bad = db.TextProperty()
    action = db.TextProperty()
    owner = db.StringProperty()
    retro_on = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)

class DayLog(db.Model):
    day = db.IntegerProperty(required=True)
    month = db.IntegerProperty(required=True)
    year = db.IntegerProperty(required=True)
    content = db.TextProperty()
    owner = db.StringProperty()
    title = db.StringProperty()
    type = db.IntegerProperty(required=True, default=DAY_LOG_DAILY)
    created_at = db.DateTimeProperty(required=True, default=datetime.datetime.now())

class AuthUser(db.Model):
    api_key = db.StringProperty()
    username = db.StringProperty()
    nickname = db.StringProperty()
    created_at = db.DateTimeProperty(required=True, default=datetime.datetime.now())
