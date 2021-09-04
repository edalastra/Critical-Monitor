from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from app.models.validators import validate_cpf

class SignupForm(FlaskForm):
    name = StringField("full_name", [DataRequired()])
    email = StringField("email", [DataRequired(), Email()])
    cpf = StringField("cpf", [DataRequired(), validate_cpf ])
    password = PasswordField("password", [DataRequired()])
    repeat_password = PasswordField("repeat_password", 
        [DataRequired(), EqualTo('password', message='As senhas não são iguais')])
