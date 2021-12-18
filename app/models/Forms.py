''' Forms for the application '''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models.validators import validate_cpf, unique_email, unique_cpf, check_password

class SigninForm(FlaskForm):
    ''' Form for signin '''
    cpf = StringField("cpf", [DataRequired()])
    password = PasswordField("password", [DataRequired()])
    remember_me = BooleanField("remember_me")

class SignupForm(FlaskForm):
    ''' Form for signup '''
    name = StringField("full_name", [DataRequired()])
    email = StringField("email", [DataRequired(), Email(), unique_email ])
    cpf = StringField("cpf", [DataRequired(), validate_cpf, unique_cpf])
    password = PasswordField("password")
    repeat_password = PasswordField("repeat_password", 
        [EqualTo('password', message='As senhas não são iguais')])

class AlterUserForm(FlaskForm):
    ''' Form for alter user '''
    name = StringField("full_name", [DataRequired()])
    email = StringField("email", [DataRequired(), Email() ])
    cpf = StringField("cpf")

class ChangePasswordForm(FlaskForm):
    ''' Form for change password '''
    current_password = PasswordField("current_password", [DataRequired(), check_password])
    new_password = PasswordField("new_password", [DataRequired()])
    repeat_new_password = PasswordField("repeat_new_password", [EqualTo('new_password', message='As senhas não são iguais')] )  
