from flask import Flask

def create_app():
    server = Flask(__name__)
    server.config['SECRET_KEY'] = 'SECRET'
    server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    register_blueprints(server)
    register_extensions(server)
    
    return server
    
    
    
def register_blueprints(server):
    from webapp.website import server_bp
    
    server.register_blueprint(server_bp)
    
    
def register_extensions(server):
    from webapp.extensions import db, migrate, login
    
    db.init_app(server)
    login.init_app(server)
    login.login_view = 'main.login'
    migrate.init_app(server, db)