from flask import Flask
import dash
from flask_admin import Admin
from flask_login import login_required


def create_app():
    server = Flask(__name__)

    server.config['SECRET_KEY'] = 'SECRET'
    server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    register_admin(server)
    register_dashapps(server)
    register_extensions(server)
    register_blueprints(server)
    return server


def register_dashapps(app):
    from webapp.dashapp1.layout import layout

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/dashapp1/',
                         )

    with app.app_context():
        dashapp1.layout = layout

    protect_dashviews(dashapp1)


def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(dashapp.server.view_functions[view_func])


def register_admin(server):
    from webapp.extensions import db
    from webapp.models import User, AdminUser

    admin = Admin(server)
    admin.add_view(AdminUser(User, db.session))


def register_extensions(server):
    from webapp.extensions import db, migrate, login

    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)


def register_blueprints(server):
    from webapp.website import server_bp

    server.register_blueprint(server_bp)