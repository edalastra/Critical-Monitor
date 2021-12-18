''' SQL Alchemy User Model '''

import bcrypt
from app import login_manager, db

class User(db.Model):
    ''' User table '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True, unique=True )
    cpf = db.Column(db.String, nullable=True, unique=True)
    password = db.Column(db.String, nullable=True)
    config = db.relationship('Config', backref='user', lazy=True)

    def __init__(self, name, email, cpf, password):
        self.name = name
        self.email = email
        self.cpf = cpf
        self.set_password(password)

    def verify_password(self, password: str) -> bool:
        ''' Verify if password is correct '''
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def set_password(self, password: str) -> None:
        ''' Set password with encryption '''
        pwhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.password = pwhash.decode('utf8') # decode the hash to prevent is encoded twice

    @property
    def has_config(self):
        ''' Check if user has at least one config '''
        stmt = self.query.join(User.config)
        result = db.session.execute(stmt)
        return result.fetchone()

    @property
    def is_authenticated(self):
        ''' Check if user is authenticated '''
        return True

    @property
    def is_active(self):
        ''' Check if user is active '''
        return True

    @property
    def is_anomymous(self):
        ''' Check if user is anomymous '''
        return False

    def get_id(self):
        ''' Get user id '''
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.cpf


@login_manager.user_loader
def load_user(id):
    ''' Load user '''
    return User.query.get(int(id))
