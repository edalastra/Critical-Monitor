from app.models.User import User
from app import db
from flask_login import login_user, logout_user

def register(form):
    user = User(form.name.data, form.email.data, form.cpf.data, form.password.data)
    db.session.add(user)
    db.session.commit()

def login(form):
    user = User.query.filter_by(cpf=form.cpf.data).first()
    if user and user.verify_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        return user
    return None
