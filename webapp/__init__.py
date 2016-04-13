from flask import Flask
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.security import MongoEngineUserDatastore, Security

db = MongoEngine()

from webapp.models import User, Role

def register_blueprints(app):
    from webapp.views import main, users, companies, customers, projects, invoices
    app.register_blueprint(main)
    app.register_blueprint(users, url_prefix='/users')
    app.register_blueprint(companies, url_prefix='/companies')
    app.register_blueprint(customers, url_prefix='/customers')
    app.register_blueprint(projects, url_prefix='/projects')
    app.register_blueprint(invoices, url_prefix='/invoice')


def create_app(**config_overrides):
    app = Flask(__name__)
    # Load config.
    app.config.from_object('webapp.config')
    # apply overrides
    app.config.update(config_overrides)
    # Setup the database.
    db.init_app(app)
    # Setup security
    app.session_interface = MongoEngineSessionInterface(db)
    user_datastore = MongoEngineUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    register_blueprints(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
