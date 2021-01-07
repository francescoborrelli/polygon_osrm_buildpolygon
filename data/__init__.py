#  Copyright (c) 2020. AV Connect Inc.
# main app class
from flask import Flask, Markup, make_response
import flask_sqlalchemy
import flask_migrate
import flask_login

# global variables
from flask_jwt_extended import JWTManager

db = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()
login_manager = flask_login.LoginManager()
app = None

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_name)

    db.init_app(app)
    migrate.init_app(app,db)

    from . import models
    login_manager.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        from . import auth
        from . import routes
        from . import matrix_dummy
        from .assets import compile_assets
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(routes.data_bp)
        app.register_blueprint(matrix_dummy.dummy_bp)
        if app.config['FLASK_ENV'] == 'development':
            compile_assets(app)

        return app
#  Copyright (c) 2020. AV Connect Inc.

