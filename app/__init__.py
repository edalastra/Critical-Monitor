from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)


app.config.from_object('config')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager(app)



from app.models import User


from app.controllers.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
from app.controllers.cm import cm as cm_blueprint
app.register_blueprint(cm_blueprint)