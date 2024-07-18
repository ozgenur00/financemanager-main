from flask import Blueprint, render_template, redirect, session, g, flash, url_for
from forms import UserLoginForm, RegistrationForm
from app.models.user import User
from app.models import db
from sqlalchemy.exc import IntegrityError
from app.utils.auth import do_login, do_logout
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.before_app_request
def add_user_to_g():
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])
    else:
        g.user = None

@auth_bp.route('/signup', methods=['GET', 'POST'], endpoint='registration')
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter(
                (User.email == form.email.data) | (User.username == form.username.data)
            ).first()
            if existing_user:
                flash("Email or username already taken. Please choose another.", "danger")
                return render_template('signup.html', form=form)

            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            if user:
                do_login(user)
                flash("Welcome!", "success")
                return redirect(url_for('main.after_login'))
            else:
                flash("Signup failed. Please try again.", "danger")
                return render_template('signup.html', form=form)
        except IntegrityError as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('You are logged in.', 'success')
            return redirect(url_for('main.after_login'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout', endpoint='logout')
def logout():
    do_logout()
    flash("You have successfully logged out.", "success")
    return redirect(url_for('main.home'))
