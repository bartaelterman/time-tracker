import json
from mongoengine import connect
import unittest
from webapp import create_app as create_app_baseimport
from webapp.models import *


def create_app():
    return create_app_baseimport(
        MONGODB_SETTINGS={'DB': 'testing'},
        TESTING=True,
        CSRF_ENABLED=False,
        LOGIN_DISABLED=True
    )

class WebappTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app()
        self.app = app.test_client()

    def tearDown(self):
        db = connect('testing')
        db.drop_database('testing')

    def test_empty_db(self):
        rv = self.app.get('/')
        assert '302' in rv.status

    def test_empty_users(self):
        rv = self.app.get('/users/')
        assert '200' in rv.status
        assert json.loads(rv.data)['users'] == []

    def test_empty_invoice(self):
        rv = self.app.get('/invoice/')
        assert '404' in rv.status

class ModelsTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app()
        self.app = app.test_client()
        user = User(username='johndoe', email='johndoe@test.com', password='password')
        user.save()

    def tearDown(self):
        db = connect('testing')
        db.drop_database('testing')

    def test_getUser(self):
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'johndoe')