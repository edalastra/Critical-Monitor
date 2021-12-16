from app.models.User import User
from app import db
from flask_login import login_user, logout_user, current_user

def register(form):
    user = User(form.name.data, form.email.data, form.cpf.data, form.password.data)
    db.session.add(user)
    db.session.commit()

def update(form):
    user = User.query.filter_by(id=current_user.id).first()
    user.name = form.name.data
    user.email = form.email.data
    db.session.commit()

def change_user_password(form):
    user = User.query.filter_by(id=current_user.id).first()
    user.set_password(form.new_password.data)
    db.session.commit()

def login(form):
    user = User.query.filter_by(cpf=form.cpf.data).first()
    if user and user.verify_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        return user
    return None
