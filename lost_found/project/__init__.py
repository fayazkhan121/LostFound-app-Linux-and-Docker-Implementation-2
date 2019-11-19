import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()


# App initialisation
def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)

    # set config instance_relative_config=True
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)

    # register endpoints
    from project.api.auth import auth_blueprint
    from project.api.lost_found_api import lost_found_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(lost_found_blueprint)

    # shell context for flask cli
    app.shell_context_processor({'app': app, 'db': db})
    return app
