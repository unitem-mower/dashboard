from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=5)])
    password = PasswordField('Password', validators=[Length(min=8)])
    submit = SubmitField('Sing in')
    

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=5)])
    password = PasswordField('Password', validators=[Length(min=8)])
    confirm_password = PasswordField('Confirmed password', validators=[Length(min=8)])
    submit = SubmitField('Sing up')
    