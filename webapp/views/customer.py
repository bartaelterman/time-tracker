from flask import Blueprint, request, jsonify
from webapp.models import Customer

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

