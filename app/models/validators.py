from wtforms import ValidationError
from app.models.User import User

def unique_email(form, field):
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError("Esse e-mail já é cadastrado")
def unique_cpf(form, field):
    user = User.query.filter_by(cpf=field.data).first()
    if user:
        raise ValidationError("Esse CPF já é cadastrado")

def validate_cpf(form, field):
    try:
        cpf = Cpf(field.data)
    except ValueError:
        raise ValidationError("CPF inválido!")
            

class Cpf:
    def __init__(self, documento):
        documento = str(documento)
        if self.cpf_eh_Valido(documento):
            self.cpf = documento
        else:
            raise ValueError("CPF inválido!")

    def __str__(self):
        return self.format_cpf()

    def cpf_eh_Valido(self, documento):
        if len(documento) == 11:
            return True
        else:
            return False

    def format_cpf(self):
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