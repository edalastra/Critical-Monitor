from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models.validators import validate_cpf, unique_email, unique_cpf

class SigninForm(FlaskForm):
    cpf = StringField("cpf", [DataRequired()])
    password = PasswordField("password", [DataRequired()])
    remember_me = BooleanField("remember_me")

class SignupForm(FlaskForm):
    name = StringField("full_name", [DataRequired()])
    email = StringField("email", [DataRequired(), Email(), unique_email ])
    cpf = StringField("cpf", [DataRequired(), validate_cpf, unique_cpf])
    password = PasswordField("password", [DataRequired()])
    repeat_password = PasswordField("repeat_password", 
        [DataRequired(), EqualTo('password', message='As senhas não são iguais')])

class ConfigForm(FlaskForm):
    minimum_distance = IntegerField("minimum_distance", [DataRequired()])
    camera_address = StringField("camera_address", [DataRequired()])