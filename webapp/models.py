from datetime import date, datetime, timedelta
from flask import url_for
from jinja2 import Template
import mongoengine
import pandas as pd
from webapp import db
from flask.ext.security import UserMixin, RoleMixin

class Role(db.Document, RoleMixin):
    """
    A role is used to determine the access level and permissions of a given user.
    """
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

class User(db.Document, UserMixin):
    """
    User class.
    """
    created_at = db.DateTimeField(default=datetime.now, required=True)
    username = db.StringField(max_length=255, required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    password = db.StringField(max_length=255)

    def get_absolute_url(self):
        return url_for('user', kwars={'username': self.username})

    def serialize(self):
        """
        Serialize this object

        :return: dict with keys `username`, `email` and `created_at`
        """
        return {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

    def __unicode__(self):
        return self.username

    meta = {
        'indexes': ['username'],
        'ordering': ['username']
    }

class Team(db.Document):
    """
    A team contains a number of members within a given company. A team can work together on a project.
    """
    name = db.StringField(max_length=255, required=True, unique=True)
    members = db.ListField(db.ReferenceField(User))

    def serialize(self):
        """
        Serialize this oject

        :return: dict with keys `name`, `members` (list)
        """
        return {
            'name': self.name,
            'members': [x.serialize() for x in self.members]
        }

    def __unicode__(self):
        return self.name


class Company(db.Document):
    """
    Company that executes work for a customer. A company can contain zero or more teams.
    """
    created_at = db.DateTimeField(default=datetime.now, required=True)
    name = db.StringField(max_length=255, required=True, unique=True)
    address = db.StringField(max_length=500, required=True)
    registration_number = db.StringField(max_length=50, required=True)
    account_number = db.StringField(max_length=50, required=True)
    teams = db.ListField(db.ReferenceField(Team))
    invoice_template = db.StringField(max_length=1000, required=False)

    def serialize(self):
        """
        Serialize this object

        :return: dict with keys `name`, `address`, `registration_number`, `account_number`, `teams` (list), `created_at`
        """
        return {
            'name': self.name,
            'address': self.address,
            'registration_number': self.registration_number,
            'account_number': self.account_number,
            'teams': [x.serialize() for x in self.teams],
            'created_at': self.created_at
        }

    def find_team(self, teamname):
        """
        Find a team in this company's list of teams

        :param teamname: the name of the team
        :return: the team. If the team is not found, a RuntimeError is raised.
        """
        queryset = []
        for t in self.teams:
            if t.name == teamname:
                queryset.append(t)
        if len(queryset) != 1:
            raise RuntimeError('find_team for {0} failed'.format(teamname))
        return queryset[0]

    def remove_team(self, teamname):
        """
        Removes a given team from this company's list of teams

        :param teamname: the name of the team
        """
        for t in self.teams:
            if t.name == teamname:
                self.teams.remove(t)

    def __unicode__(self):
        return self.name

class Customer(db.Document):
    """
    Customer for who a project is being done. All billing details should be set here.
    """
    created_at = db.DateTimeField(default=datetime.now, required=True)
    name = db.StringField(max_length=255, required=True, unique=True)
    address = db.StringField(max_length=500, required=True)
    registration_number = db.StringField(max_length=50, required=True)

    def serialize(self):
        """
        Serialize this object

        :return: dict with parameters `name`, `address`, `registration_number`
        """
        return {
            'name': self.name,
            'address': self.address,
            'registration_number': self.registration_number
        }

    def __unicode__(self):
        return self.name

class Activity(db.Document):
    """
    A limited amount of work done by a user on a given date and time.
    """
    user = db.ReferenceField(User, reverse_delete_rule=mongoengine.CASCADE)
    start = db.DateTimeField(required=True)
    minutes = db.IntField(required=True)
    description = db.StringField(max_length=255, required=False)
    billable = db.BooleanField(default=True)

    def serialize(self):
        """
        Serialize this object

        :return: dict with parameters `id`, `user`, `start`, `duration_str`, `minutes`, `description`, `billable`
        """
        return {
            'id': str(self.id),
            'user': self.user.serialize(),
            'start': self.start.isoformat(),
            'duration_str': '{0} minutes'.format(self.minutes),
            'minutes': self.minutes,
            'description': self.description,
            'billable': self.billable
        }

    def __unicode__(self):
        return '{0} {1}'.format(self.user.username, self.start.isoformat())

class Project(db.Document):
    """
    A project done by a given team in a company for a customer. Team members can log activities done for a given
    project. A project also contains an agreed on hourly rate for billing.
    """
    created_at = db.DateTimeField(default=datetime.now, required=True)
    name = db.StringField(max_length=255, required=True, unique=True)
    customer = db.ReferenceField(Customer, reverse_delete_rule=mongoengine.CASCADE, required=True)
    company = db.ReferenceField(Company, required=True)
    team = db.ReferenceField(Team, reverse_delete_rule=mongoengine.CASCADE, required=True)
    activities = db.ListField(db.ReferenceField(Activity))
    hourly_rate = db.FloatField(required=False)

    def serialize(self):
        """
        Serializes this object

        :return: dict with parameters `name`, `customer`, `company`, `hourly_rate`, `team` and a list of `activities`
        """
        return {
            'name': self.name,
            'customer': self.customer.name,
            'company': self.company.name,
            'hourly_rate': self.hourly_rate,
            'team': self.team.serialize(),
            'activities': [x.serialize() for x in self.activities]
        }

    def invoice_serialize(self):
        """
        Serializes a limited number of attributes of this object, required for generating an invoice.

        :return: dict with parameters `name` and `hourly_rate`
        """
        return {
            'name': self.name,
            'hourly_rate': self.hourly_rate,
        }

    def find_activity(self, activityid):
        """
        Find an activity in this projects list of activities

        :param activityid: the id of the activity
        :return: the activity. If the activity is not found, a RuntimeError is raised.
        """
        queryset = []
        for a in self.activities:
            if a.id == activityid:
                queryset.append(a)
        if len(queryset) != 1:
            raise RuntimeError('find_activity for {0} failed'.format(activityid))
        return queryset[0]

    def remove_activity(self, activityid):
        """
        Removes a given activity from this projects list of activities

        :param activityid: the id of the activity
        """
        for a in self.activities:
            if a.id == activityid:
                self.activities.remove(a)

    def get_activities_dict(self, start_date, end_date, only_billable=True):
        """
        Returns activities within requested date range. Note that both start_date and end_date are included.

        :param start_date: datetime.date object that marks the start of the interval of interest.
        :param end_date: datetime.date object that marks the end of the interval of interest.
        :param only_billable: boolean. Default=True. Whether to return only billable activities
        :return: a dictionary with `sum` being the total amount of minutes spent, and `activities` being a list of activities.
        """
        queryset = []
        total = 0
        for a in self.activities:
            if a.start >= start_date and a.start <= end_date:
                if (not only_billable) or (only_billable and a.billable):
                    queryset.append(a.serialize())
                    total += a.minutes
        return {'sum': total, 'activities': queryset}

    def get_activities_df(self, start_date, end_date, only_billable=True):
        """
        Returns activities within requested date range as a pandas.DataFrame. Note that both start_date and end_date are included.

        :param start_date: datetime.date object that marks the start of the interval of interest.
        :param end_date: datetime.date object that marks the end of the interval of interest.
        :param only_billable: boolean. Default=True. Whether to return only billable activities
        :return: a pandas.DataFrame containing the matched activities' start, minutes, description and billable information.
        """
        queryset = []
        for a in self.activities:
            if a.start >= start_date and a.start <= end_date:
                if (not only_billable) or (only_billable and a.billable):
                    queryset.append(
                        {'start': a.start,
                         'minutes': a.minutes,
                         'billable': a.billable,
                         'description': a.description
                         }
                    )
        return pd.DataFrame(queryset)

    def get_activities_by_week(self, start_date, end_date, only_billable=True):
        """
        Returns activities within requested date range aggregated by week.

        :param start_date: datetime.date object that marks the start of the interval of interest.
        :param end_date: datetime.date object that marks the end of the interval of interest.
        :param only_billable: boolean. Default=True. Whether to return only billable activities
        :return: a pandas.DataFrame containing the matched activities' start, minutes, description and billable information.
        """
        activities = self.get_activities_df(start_date, end_date, only_billable=only_billable)
        activities['weeknr'] = activities['start'].apply(lambda x: x.isocalendar()[1])
        activities['weekstart'] = activities['start'].apply(lambda x: (x - timedelta(days=x.weekday())).date())
        activities['weekend'] = activities['start'].apply(lambda x: (x + timedelta(days=(6 - x.weekday()))).date())
        result = activities[['weeknr', 'weekstart', 'weekend', 'minutes']].groupby(['weeknr', 'weekstart', 'weekend']).sum()
        index = result.index.values
        result.index = pd.Index(range(0, len(index)))
        result['weeknr'] = pd.Series(index).apply(lambda x: x[0])
        result['weekstart'] = pd.Series(index).apply(lambda x: x[1])
        result['weekend'] = pd.Series(index).apply(lambda x: x[2])
        return result


    def generate_invoice(self, start_date, end_date, template=None):
        """
        Returns an invoice as html for a given period.

        :param start_date: datetime.date object that marks the start of the interval of interest.
        :param end_date: datetime.date object that marks the end of the interval of interest.
        :param template: a jinja2 template string. If not given, the projects own invoice_template is used.
        :return: The invoice as html for a given period.
        """
        activities_df = self.get_activities_by_week(start_date, end_date)
        total_minutes = activities_df['minutes'].sum()
        total_amount = (total_minutes / 60.0) * self.hourly_rate
        activities_list = activities_df.T.to_dict().values()
        invoice_date = date.today().isoformat()
        if template is None:
            template = Template(self.invoice_template)
        else:
            template = Template(template)
        return template.render(activities=activities_list,
                        company=self.company.serialize(),
                        customer=self.customer.serialize(),
                        invoice_date=invoice_date,
                        project=self.invoice_serialize(),
                        total=total_amount)
