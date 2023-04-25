from flask import Flask
import dash
from flask.helpers import get_root_path
from flask_admin import Admin


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
    
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/data/',
                         assets_folder=get_root_path(__name__) + '/data/assets/',
                         meta_tags=[meta_viewport])

    with app.app_context():
        dashapp1.title = 'Dashapp 1'
        dashapp1.layout = layout
  

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