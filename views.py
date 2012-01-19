import sys
import types
import base64
import secret
import logging
import functools
from google.appengine.ext import db
from google.appengine.ext import webapp
from django.utils import simplejson
from models import *

logger = logging.getLogger(__name__)

def basic_auth(fn_or_role):
    def decorator(role, fn):
        @functools.wraps(fn)
        def wrapper(webappRequest, *args, **kwargs):
            if _auth_user(webappRequest, role):
                return fn(webappRequest, *args, **kwargs)
            webappRequest.response.set_status(401, message="Authorization Required")
            webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="eLogger"'

        return wrapper

    if type(fn_or_role) is types.FunctionType:
        return decorator(None, fn_or_role)
    return lambda f: decorator(fn_or_role, f)


class AuthUserHandler(webapp.RequestHandler):
    @basic_auth('admin')
    def post(self):
        self._add_user(simplejson.loads(self.request.body))

    def _add_user(self, user_dict):
        user = AuthUser.get_by_key_name(user_dict['userid'])
        now = datetime.datetime.now()
        if user:
            # TODO fixme, seems not work below lines
            user.last_login_at = now
            user.username = user_dict['username'],
            user.nickname = user_dict['nickname'],
            user.api_key = user_dict['api_key'],
        else:
            user = AuthUser(
                key_name=user_dict['userid'],
                username=user_dict['username'],
                nickname=user_dict['nickname'],
                api_key=user_dict['api_key'],
                created_at=now,
                last_login_at=now,
            )
        user.put()


class RetroHandler(webapp.RequestHandler):
    @basic_auth
    def get(self):
        retros = db.GqlQuery("SELECT * FROM Retro WHERE owner = :1 ORDER BY retro_on DESC, created_on DESC",
            owner=self.user.key_name)
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
        self._add_retro(simplejson.loads(self.request.body))
        self.response.set_status(202)
        self.response.out.write("")

    def _add_retro(self, retro_dict):
        retro = Retro()
        retro.goal = retro_dict.get('goal')
        retro.good = retro_dict.get('good')
        retro.bad = retro_dict.get('bad')
        retro.action = retro_dict.get('action')
        retro.owner = self.user.key_name
        retro.retro_on = retro_dict.get('retro_on')
        retro.put()


class DayLogHandler(webapp.RequestHandler):
    @basic_auth
    def get(self):
        year = int(self.request.get('year'))
        month = int(self.request.get('month'))
        # check args
        day_logs = self._get_month_logs(month, year)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(
            simplejson.dumps(
                [{'day': day_log.day,
                  'content': day_log.content,
                  'title': day_log.title,
                  'type': day_log.type,
                  'id': day_log.key().id()
                } for day_log in day_logs]))

    @basic_auth
    def post(self):
        id = self._save_day_log(simplejson.loads(self.request.body))
        logger.info('saved daylog[%s]', id)
        self.response.out.write(id)
        self.response.set_status(200)

    def _get_month_logs(self, month, year):
        day_logs = db.GqlQuery(
            "SELECT * FROM DayLog WHERE owner = :1 AND year = :2 AND month= :3 ORDER BY day DESC, type ASC, created_at DESC"
            ,
            self.user.key().name(), year, month)
        return day_logs

    def _save_day_log(self, log_dict):
        daylog = db.GqlQuery(
            "SELECT * FROM DayLog WHERE owner = :1 AND year = :2 AND month= :3 AND day= :4",
            self.user.key().name(),
            log_dict.get('year'),
            log_dict.get('month'),
            log_dict.get('day'),
        ).get()
        if daylog:
            daylog.content = log_dict.get('content')
        else:
            daylog = DayLog(
                owner=self.user.key().name(),
                day=log_dict.get('day'),
                month=log_dict.get('month'),
                year=log_dict.get('year'),
                content=log_dict.get('content'),

            )
        daylog.put()
        return daylog.key().id()


def _auth_user(webappRequest, role=None):
    auth_header = webappRequest.request.headers.get('Authorization')
    if not auth_header:
        return False
    auth_parts = auth_header.split(' ')
    user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
    userid = user_pass_parts[0]
    api_key = user_pass_parts[1]
    if role == 'admin':
        return userid == secret.ADMIN and api_key == secret.MASTER_KEY

    user = AuthUser.get_by_key_name(userid)

    if not user or (api_key != user.api_key and api_key != secret.MASTER_KEY):
        return False
    webappRequest.user = user
    return True


class MigrateHandler(webapp.RequestHandler):
    @basic_auth('admin')
    def post(self):
        action = self.request.get('action')
        if not action:
            self.response.out.write("no action specified")
            self.response.set_status(400)

        actions = {
            'refresh_daylog_type': self._refresh_daylog_type,
            'migrate_owners': self._migrate_owners,
            }

        if action in actions:
            if actions[action]():
                self.response.out.write('action %s done!' % action)
                self.response.set_status(200)

        else:
            self.response.out.write("'%s' is not an available migration" % action)
            self.response.set_status(400)

    # TODO remove after done
    def _migrate_owners(self):
        for day_log in db.GqlQuery("SELECT * FROM DayLog WHERE owner = :1", 'weibo/nanfang05'):
            day_log.owner='weibo/2053167845'
            day_log.put()
        return True

    def _refresh_daylog_type(self):
        for day_log in DayLog.all():
        #            if day_log.type is not None:
            day_log.type = DAY_LOG_DAILY
            day_log.created_at = datetime.datetime.now()
            day_log.put()
            logger.info('migrate daylog[%s-%s-%s]', day_log.year, day_log.month, day_log.day)
        return True
