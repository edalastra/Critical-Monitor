from app import login_manager, db
import bcrypt   

class User(db.Model):
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

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def set_password(self, password):
        pwhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        self.password = pwhash.decode('utf8') # decode the hash to prevent is encoded twice

    @property
    def has_config(self):
        stmt = self.query.join(User.config)
        result = db.session.execute(stmt)
        return result.fetchone()

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
    