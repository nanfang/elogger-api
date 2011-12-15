import base64
import keys
import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
from models import *

logger=logging.getLogger(__name__)

class RetroHandler(webapp.RequestHandler):
    @basic_auth
    def get(self):
        retros = db.GqlQuery("SELECT * FROM Retro WHERE owner = :1 ORDER BY retro_on DESC, created_on DESC", owner=self.user.key_name)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
                simplejson.dumps(
                        [{
                          'id': retro.key().id(),
                          'goal': retro.goal or '',
                          'good': retro.good or '',
                          'bad': retro.bad or '',
                          'action': retro.action or '',
                          'retro_on': retro.retro_on or '',
                         } for retro in retros]))

    @basic_auth
    def post(self):
        logger.info(self.request.body)
        self._add_retro(simplejson.loads(self.request.body))
        self.response.set_status(202)
        self.response.out.write("")

    def _add_retro(self, retro_dict):
        retro=Retro()
        retro.goal=retro_dict.get('goal')
        retro.good=retro_dict.get('good')
        retro.bad=retro_dict.get('bad')
        retro.action=retro_dict.get('action')
        retro.owner=self.user.key_name
        retro.retro_on=retro_dict.get('retro_on')
        retro.put()

class DayLogHandler(webapp.RequestHandler):
    @basic_auth
    def get(self):
        year = int(self.request.get('year'))
        month = int(self.request.get('month'))
        day_logs = self._get_month_logs(month, year)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            simplejson.dumps(
                [{'day': day_log.day,
                  'content': day_log.content,
                  'plan': day_log.plan,
                  } for day_log in day_logs]))

    @basic_auth
    def post(self):
        self._save_day_log(simplejson.loads(self.request.body))
        self.response.set_status(200)

    def _get_month_logs(self, month, year):
        day_logs = db.GqlQuery(
            "SELECT * FROM DayLog WHERE owner = :1 AND year = :2 AND month= :3 ORDER BY day DESC",
            self.user, year, month)
        return day_logs

    def _save_day_log(self, log_dict):
        day_log = DayLog()
        day_log.day = log_dict.get('day')
        day_log.month = log_dict.get('month')
        day_log.year = log_dict.get('year')
        day_log.content = log_dict.get('content')
        day_log.plan = log_dict.get('plan')
        day_log.put()
        
def basic_auth(func):
    def callf(webappRequest, *args, **kwargs):
        if _auth_user(webappRequest):
            return func(webappRequest, *args, **kwargs)
        webappRequest.response.set_status(401, message="Authorization Required")
        webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="eLogger"'
    return callf

def _auth_user(webappRequest):
    auth_header = webappRequest.request.headers.get('Authorization')
    if not auth_header:
        return False
    
    auth_parts = auth_header.split(' ')
    user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
    username = user_pass_parts[0]
    api_key = user_pass_parts[1]
    user = AuthUser.get_by_key_name(username)

    if not user or (api_key != user.api_key and api_key != keys.master_key):
        return False
    
    webappRequest.user = user
    
    return True

