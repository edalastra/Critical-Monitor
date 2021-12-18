''' Form validator functions '''

from wtforms import ValidationError
from flask_login import current_user
from app.models import User

def check_password(form, field):
    ''' Check if password is correct '''
    print('validada')
    if not current_user.verify_password(field.data):
        raise ValidationError("Senha incorreta!")

def unique_email(form, field):
    ''' Check if email is unique '''
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError("Esse e-mail já é cadastrado")

def unique_cpf(form, field):
    ''' Check if cpf is unique '''
    user = User.query.filter_by(cpf=field.data).first()
    if user:
        raise ValidationError("Esse CPF já é cadastrado")

def validate_cpf(form, field):
    ''' Check if cpf is valid '''
    try:
        Cpf(field.data)
    except ValueError:
        raise ValidationError("CPF inválido!")

class Cpf:
    ''' cpf validator '''
    def __init__(self, documento):
        documento = str(documento)
        if self.cpf_eh_Valido(documento):
            self.cpf = documento
        else:
            raise ValueError("CPF inválido!")

    def __str__(self):
        return self.format_cpf()

    def cpf_eh_Valido(self, documento: str) -> bool:
        ''' Check if cpf is valid '''
        if len(documento) == 11:
            return True
        else:
            return False

    def format_cpf(self) -> str:
        ''' Format cpf '''
        fatia_um = self.cpf[:3]
        fatia_dois = self.cpf[3:6]
        fatia_tres = self.cpf[6:9]
        fatia_quatro = self.cpf[9:]
        return(
            "{}.{}.{}-{}".format(
                fatia_um,
                fatia_dois,
                fatia_tres,
                fatia_quatro
            )
        )
