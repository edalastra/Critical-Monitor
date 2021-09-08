from flask import Blueprint

cm = Blueprint('cm', __name__) 

cm.route('/home')
def home():
    return 'ta logado bixo'