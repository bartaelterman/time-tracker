from flask import Blueprint, request, jsonify
from webapp.models import User, Company, Team, Customer, Project, Activity
from time import strptime
from datetime import datetime

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
            user = User.objects.get(username=request.json.get('username'))
            start_datetime = datetime(*strptime(request.json.get('start'), '%Y-%m-%d %H:%M:%S')[0:6])
            if request.json.get('billable') == 'true':
                billable = True
            elif request.json.get('billable') == 'false':
                billable = False
            else:
                raise ValueError('billable should be "true" or "false"')
            activity = Activity(
                user=user,
                start=start_datetime,
                minutes=request.json.get('minutes'),
                description=request.json.get('description'),
                billable=billable
            )
            activity.save()
            project.modify(push__activities=activity)
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
