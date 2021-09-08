from app import db
from flask_login import login_user, logout_user
from flask import Blueprint, render_template, flash, redirect, url_for
from app.models.Forms import SignupForm, SigninForm
from app.models.User import User

auth = Blueprint('user', __name__) 


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(cpf=form.cpf.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("/home"))

        flash("CPF ou senha incorretos.")
    return render_template('signin.html', form_signin=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        
        user = User(form.name.data, form.email.data, form.cpf.data, form.password.data)
        db.session.add(user)
        db.session.commit()

        redirect("user.signin")

    return render_template('signup.html', form_signup=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("user.signin"))