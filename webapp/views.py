from flask import Blueprint, request, render_template, jsonify, abort
from flask_security import login_required
from webapp.models import User, Company, Team, Customer, Project, Activity
from time import strptime
from webapp.template_strings import DEFAULT_INVOICE
from datetime import datetime

# = = = = = = = = = = = = = =
# USERS BLUEPRINT
# = = = = = = = = = = = = = =
users = Blueprint('user', __name__)

@users.route('/', methods=['GET', 'POST'])
def list_users():
    """
       List all users / Create a new user

    **Example output**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: text/javascript

        {
            username: "John Doe",
            email: "johndoe@gmail.com"
        }
    """

    if request.method == 'GET':
        users = User.objects.all()
        return jsonify(users=[u.serialize() for u in users])
    elif request.method == 'POST':
        try:
            user = User(
                username=request.form.get('username'),
                email=request.form.get('email')
            )
            user.save()
        except:
            return 'incorrect data format', 400
        return 'OK'

@users.route('/<username>', methods=['GET', 'PUT', 'DELETE'])
def get_user(username):
    """
    Get, update or delete the user matching the given username

    :param username: string
    :return: nothing in case of DELETE, otherwise the serialized :class:`User <User>` object is returned
    """
    user = User.objects.get_or_404(username=username)
    if request.method == 'PUT':
        try:
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.save()
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        user.delete()
        return 'user deleted'
    return jsonify(user.serialize())


# = = = = = = = = = = = = = =
# COMPANIES BLUEPRINT
# = = = = = = = = = = = = = =
companies = Blueprint('company', __name__)

@companies.route('/', methods=['GET', 'POST'])
def list_companies():
    if request.method == 'GET':
        companies = Company.objects.all()
        return jsonify(companies=[c.serialize() for c in companies])
    elif request.method == 'POST':
        try:
            comp = Company(
                name=request.form.get('name'),
                address=request.form.get('address'),
                registration_number=request.form.get('registration_number'),
                account_number=request.form.get('account_number')
            )
            comp.save()
        except:
            return 'incorrect data format', 400
        return 'OK'

@companies.route('/<companyname>', methods=['GET', 'PUT', 'DELETE'])
def get_company(companyname):
    company = Company.objects.get_or_404(name=companyname)
    if request.method == 'PUT':
        try:
            company.update(name=request.form.get('name'))
            company.update(address=request.form.get('address'))
            company.update(registration_number=request.form.get('registration_number'))
            company.update(account_number=request.form.get('account_number'))
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        company.delete()
        return 'OK'
    return jsonify(company.serialize())

@companies.route('/<companyname>/teams', methods=['GET', 'POST'])
def list_teams(companyname):
    company = Company.objects.get_or_404(name=companyname)
    if request.method == 'GET':
        return jsonify(teams=[t.serialize() for t in company.teams])
    elif request.method == 'POST':
        try:
            team = Team(name=request.form.get('name'))
            members = [User.objects.get(username=x) for x in request.form.get('members').split(';')]
            team.members = members
            team.save()
            company.teams.append(team)
            company.save()
        except Exception, e:
            print e.message
            return 'incorrect data format', 400
        return 'OK'

@companies.route('/<companyname>/teams/<teamname>', methods=['GET', 'PUT', 'DELETE'])
def get_team(companyname, teamname):
    company = Company.objects.get_or_404(name=companyname)
    team = company.find_team(teamname)
    if request.method == 'PUT':
        try:
            team.name = request.form.get('name')
            team.members = [User.objects.get(username=x) for x in request.form.get('members').split(';')]
            company.remove_team(teamname)
            company.teams.append(team)
            company.save()
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        company.remove_team(teamname)
        company.save()
    return jsonify(team.serialize())


# = = = = = = = = = = = = = =
# CUSTOMERS BLUEPRINT
# = = = = = = = = = = = = = =
customers = Blueprint('customer', __name__)

@customers.route('/', methods=['GET', 'POST'])
def list_customers():
    if request.method == 'GET':
        customers = Customer.objects.all()
        return jsonify(customers=[c.serialize() for c in customers])
    elif request.method == 'POST':
        try:
            customer = Customer(
                name=request.form.get('name'),
                address=request.form.get('address'),
                registration_number=request.form.get('registration_number'),
            )
            customer.save()
        except:
            return 'incorrect data format', 400
        return 'OK'

@customers.route('/<customername>', methods=['GET', 'PUT', 'DELETE'])
def get_customer(customername):
    customer = Customer.objects.get_or_404(name=customername)
    if request.method == 'PUT':
        try:
            customer.update(name=request.form.get('name'))
            customer.update(address=request.form.get('address'))
            customer.update(registration_number=request.form.get('registration_number'))
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        customer.delete()
        return 'OK'
    return jsonify(customer.serialize())

# = = = = = = = = = = = = = =
# PROJECTS BLUEPRINT
# = = = = = = = = = = = = = =
projects = Blueprint('project', __name__)

@projects.route('/', methods=['GET', 'POST'])
def list_projects():
    if request.method == 'GET':
        projects= Project.objects.all()
        return jsonify(projects=[p.serialize() for p in projects])
    elif request.method == 'POST':
        try:
            customer = Customer.objects.get(name=request.form.get('customer'))
            company = Company.objects.get(name=request.form.get('company'))
            team = company.find_team(request.form.get('team'))
            project = Project(
                name=request.form.get('name'),
                customer=customer,
                company=company,
                team=team,
                hourly_rate=request.form.get('hourly_rate')
            )
            project.save()
        except Exception, e:
            print e.message
            return 'incorrect data format', 400
        return 'OK'

@projects.route('/<projectname>', methods=['GET', 'PUT', 'DELETE'])
def get_project(projectname):
    project = Project.objects.get_or_404(name=projectname)
    if request.method == 'PUT':
        try:
            customer = Customer.objects.get(name=request.form.get('customer'))
            company = Company.objects.get(name=request.form.get('company'))
            team = Team.objects.get(name=request.form.get('team'))
            project.update(name=request.form.get('name'))
            project.update(customer=customer)
            project.update(company=company)
            project.update(team=team)
            project.update(hourly_rate=request.form.get('hourly_rate'))
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        project.delete()
        return 'OK'
    return jsonify(project.serialize())

@projects.route('/<projectname>/activities', methods=['GET', 'POST'])
def list_activities(projectname):
    project = Project.objects.get_or_404(name=projectname)
    print project.activities
    if request.method == 'GET':
        return jsonify(activities=[a.serialize() for a in project.activities])
    elif request.method == 'POST':
        try:
            user = User.objects.get(username=request.form.get('username'))
            start_datetime = datetime(*strptime(request.form.get('start'), '%Y-%m-%d %H:%M:%S')[0:6])
            if request.form.get('billable') == 'true':
                billable = True
            elif request.form.get('billable') == 'false':
                billable = False
            else:
                raise ValueError('billable should be "true" or "false"')
            activity = Activity(
                user=user,
                start=start_datetime,
                minutes=request.form.get('minutes'),
                description=request.form.get('description'),
                billable=billable
            )
            activity.save()
            project.activities.append(activity)
            project.save()
        except Exception, e:
            print e.message
            return 'incorrect data format', 400
        return 'OK'

@projects.route('/<projectname>/activities/<activityid>', methods=['GET', 'PUT', 'DELETE'])
def get_activity(projectname, activityid):
    project = Project.objects.get_or_404(name=projectname)
    activity = Activity.objects.get_or_404(id=activityid)
    if request.method == 'PUT':
        try:
            user = User.objects.get(username=request.form.get('username'))
            start_datetime = datetime(*strptime(request.form.get('start'), '%Y-%m-%d %H:%M:%S')[0:6])
            if request.form.get('billable') == 'true':
                billable = True
            elif request.form.get('billable') == 'false':
                billable = False
            else:
                raise ValueError('billable should be "true" or "false"')
            activity.user = user
            activity.start = start_datetime
            activity.minutes=request.form.get('duration')
            activity.description=request.form.get('description')
            activity.billable=billable
            activity.save()
            project.remove_activity(activityid)
            project.activities.append(activity)
            project.save()
        except:
            return 'incorrect data format', 400
    elif request.method == 'DELETE':
        project.remove_activity(activityid)
        project.save()
        activity.delete()
        return 'OK'
    return jsonify(activity.serialize())

# = = = = = = = = = = = = = =
# INVOICES BLUEPRINT
# = = = = = = = = = = = = = =
invoices = Blueprint('invoice', __name__)

@invoices.route('/', methods=['GET'])
@login_required
def get_invoice():
    projectname = request.args.get('project')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    print 'requested project: {0}'.format(projectname)
    print 'requested period: {0} - {1}'.format(start_date, end_date)

    if request.method == 'GET':
        project = Project.objects.get_or_404(name=projectname)
        try:
            start_dt = datetime(*strptime(start_date, '%Y-%m-%d')[0:6])
            end_dt = datetime(*strptime(end_date, '%Y-%m-%d')[0:6])
        except Exception, e:
            print e.message
            abort(400)
        if request.args.get('format') == 'json':
            activities = project.get_activities_dict(start_dt, end_dt, only_billable=True)
            return jsonify(
                activities=activities,
                customer=project.customer.serialize(),
                company=project.company.serialize(),
                project=project.serialize()
            )
        else:
            template = project.generate_invoice(start_dt, end_dt, template=DEFAULT_INVOICE)
            return template
