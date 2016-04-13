from flask import Blueprint, request, jsonify
from webapp.models import User
from mongoengine.errors import ValidationError

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
                username=request.json.get('username'),
                email=request.json.get('email')
            )
            user.save()
        except ValidationError, e:
            print e.message
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

