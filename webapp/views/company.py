from flask import Blueprint, request, jsonify
from webapp.models import User, Company, Team

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
