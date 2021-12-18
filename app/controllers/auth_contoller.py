''' auth controller '''
from flask_login import login_user, current_user
from app.models import User
from app import db

def register(form):
    '''
        Register a new user
    '''
    user = User(form.name.data, form.email.data, form.cpf.data, form.password.data)
    db.session.add(user)
    db.session.commit()

def update(form):
    '''
        Update user profile
    '''
    user = User.query.filter_by(id=current_user.id).first()
    user.name = form.name.data
    user.email = form.email.data
    db.session.commit()

def change_user_password(form):
    '''
        Change user password
    '''
    user = User.query.filter_by(id=current_user.id).first()
    user.set_password(form.new_password.data)
    db.session.commit()

def login(form):
    '''
        Login user
    '''
    user = User.query.filter_by(cpf=form.cpf.data).first()
    if user and user.verify_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        return user
    return None
