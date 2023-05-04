from flask import Blueprint, render_template, redirect, url_for
from webapp.forms import LoginForm, RegisterForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import User
from webapp.extensions import db



server_bp = Blueprint('main', __name__)


@server_bp.route("/")
@server_bp.route("/home")
def home():
    if current_user.is_anonymous:
        return redirect(url_for('main.login'))
    return render_template("home.html", title="home page")


@server_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Invalid username or password'
            return render_template("login.html", form=form, error=error)

        login_user(user)
        return redirect(url_for('main.home'))

    return render_template("login.html", title="login page", form=form)


@server_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()

    if form.validate_on_submit() and form.password.data == form.confirm_password.data:
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.create_all()
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.home'))

    return render_template("register.html", title="register", form=form)

@server_bp.route("/dashapp1/")
# @server_bp.route("/home")
def dash():
    if current_user.is_anonymous:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.dashboard1'))


@server_bp.route("/logout")
@login_required
def logout():
    logout_user()



    return redirect(url_for('main.home'))