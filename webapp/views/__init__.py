from flask import Blueprint, redirect

from .user import users, list_users, get_user
from .company import companies, get_company, list_companies, get_team, list_teams
from .customer import customers, get_customer, list_customers
from .project import projects, get_project, list_projects, get_activity, list_activities
from .invoice import invoices, get_invoice

# = = = = = = = = = = = = = =
# MAIN BLUEPRINT
# = = = = = = = = = = = = = =
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def main_view():
    return redirect('/static/index.html')

@main.route('/track', methods=['GET'])
def track_time():
    return redirect('/static/track.html')