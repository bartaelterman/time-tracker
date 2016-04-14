from datetime import datetime
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
        self.user = User(username='johndoe', email='johndoe@test.com', password='password')
        self.user.save()
        self.company = Company(name='testcomp', address='some street', registration_number='1', account_number='BE4942')
        self.company.save()
        self.customer = Customer(name='testcustomer', address='street2', registration_number='42')
        self.customer.save()
        self.team = Team(name='testteam', members=[self.user])
        self.team.save()

    def tearDown(self):
        db = connect('testing')
        db.drop_database('testing')

    def test_getUser(self):
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['username'], 'johndoe')

    def test_delete_activity(self):
        project = Project(name='testproject', customer=self.customer, company=self.company, team=self.team)
        project.save()
        activity = Activity(user=self.user, start=datetime(2010, 1, 1, 10, 0, 0), minutes=40,
                            description='test activity', billable=True)
        activity.save()
        project.modify(push__activities=activity)
        # confirm that the modified project is persisted by checking the number of activities
        p2 = Project.objects.get(name='testproject')
        self.assertEqual(len(p2.activities), 1)
        # now remove the activity from the project and check again
        project.remove_activity(activity.id)
        p2 = Project.objects.get(name='testproject')
        self.assertEqual(len(p2.activities), 0)

