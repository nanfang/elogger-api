from google.appengine.ext import db

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
    plan = db.TextProperty()
    owner = db.StringProperty()

class AuthUser(db.Model):
    api_key = db.StringProperty()

