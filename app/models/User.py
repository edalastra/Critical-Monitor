from app import login_manager, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=True, unique=True )
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    cpf = db.Column(db.String, nullable=True, unique=True)
    password = db.Column(db.String, nullable=True)


    def __init__(self, id, first_name, last_name, cpf):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.cpf = cpf
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
       return '<User %r>' % self.cpf
    