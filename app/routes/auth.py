from app import db, login_manager
from flask_login import login_user, logout_user, current_user
from flask import Blueprint, render_template, flash, redirect, url_for
from app.models.Forms import SignupForm, SigninForm
from app.models.User import User
from app.controllers.auth_contoller import register, login

auth = Blueprint('auth', __name__) 


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('monitor.home'))
    form = SigninForm()
    if form.validate_on_submit():
        if login(form):
            print('Login Successful')
            return redirect(url_for('monitor.home'))
        flash("CPF ou senha incorretos.")
    return render_template('auth/signin.html', form_signin=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('monitor.home'))
    form = SignupForm()

    if form.validate_on_submit():
        register(form)
        redirect(url_for('monitor.auth.signin'))

    return render_template('auth/signup.html', form_signup=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('monitor.auth.signin')) 

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('monitor.auth.signin'))