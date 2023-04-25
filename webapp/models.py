from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from webapp.extensions import db, login

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def __repr__(self):
        return '<User {}>'.format(self.username)   


class AdminUser(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated