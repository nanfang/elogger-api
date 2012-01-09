import unittest
import base64
from gaetestbed import FunctionalTestCase
from django.utils import simplejson
from models import *
from app import application
import secret

class APITest(FunctionalTestCase, unittest.TestCase):

    APPLICATION = application
    def setUp(self):
        self._init_test_data()

    def test_should_save_and_get_daylog(self):
        data = {
            'day':18,
            'month':12,
            'year':2011,
            'content':'get API test done',
            'plan':'no plan'
        }
        response = self.post('/daylogs', data=data)
        self.assertEquals(response.status, "401 Authorization Required")
        response = self.post('/daylogs', simplejson.dumps(data),
                content_type = 'application/json', headers={'Authorization':self._auth_header('elogger/test', 'test')})
        self.assertEquals(response.status, "200 OK")
        response = self.get('/daylogs', {'year':2011, 'month':12},  headers={'Authorization':self._auth_header('elogger/test', 'test')})
        self.assertEquals(response.body, '[{"content": "get API test done", "day": 18, "plan": "no plan"}]')
                
    def _auth_header(self, user, pwd):
        return 'Basic %s' % base64.b64encode('%s:%s' % (user, pwd))

    def _init_test_data(self):
        self.post('/users', simplejson.dumps({'username':'elogger/test', 'api_key':'test'}),
            headers={'Authorization':self._auth_header(secret.ADMIN, secret.MASTER_KEY)})

if __name__ == '__main__':
    unittest.main()
