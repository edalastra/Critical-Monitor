from app import login_manager, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True, unique=True )
    cpf = db.Column(db.String, nullable=True, unique=True)
    password = db.Column(db.String, nullable=True)


    def __init__(self, first_name, last_name, email, cpf, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.cpf = cpf
        self.password = password
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anomymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
       return '<User %r>' % self.cpf
    