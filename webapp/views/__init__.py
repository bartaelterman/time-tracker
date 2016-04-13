from flask import Blueprint, request, jsonify, abort, redirect
from flask_security import login_required
from webapp.models import Project
from time import strptime
from webapp.template_strings import DEFAULT_INVOICE
from datetime import datetime

from .user import users, list_users, get_user
from .company import companies, get_company, list_companies, get_team, list_teams
from .customer import customers, get_customer, list_customers
from .project import projects, get_project, list_projects, get_activity, list_activities


# = = = = = = = = = = = = = =
# MAIN BLUEPRINT
# = = = = = = = = = = = = = =
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def main_view():
    return redirect('/static/index.html')


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
