from flask import request, make_response, jsonify
import flask
from app import db, login_manager
from flask_login import login_user, logout_user, current_user, login_required
from flask import Blueprint, render_template, flash, redirect, url_for
from app.models.Forms import AlterUserForm, SignupForm, SigninForm, ChangePasswordForm
from app.models.User import User
from app.controllers.auth_contoller import register, login, update, change_user_password

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
        flash("CPF ou senha incorretos.", 'danger')
    return render_template('auth/signin.html', form_signin=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        register(form)
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.signin'))
    return render_template('auth/signup.html', form_signup=form )

@auth.route('/profile/edit', methods=['GET','POST'])
@login_required
def edit_profile():
    form_user = AlterUserForm()
    if form_user.validate_on_submit():
        update(form_user)
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.edit_profile'))
    return render_template('auth/edit_profile.html', form_user=form_user)

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form_password = ChangePasswordForm()
    if form_password.validate_on_submit():
        change_user_password(form_password)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('auth.edit_profile'))
    return render_template('auth/change_password.html', form_password=form_password)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.signin')) 

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.signin'))