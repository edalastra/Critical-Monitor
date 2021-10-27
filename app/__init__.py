from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__)


app.config.from_object('config')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager(app)

socketio = SocketIO(app)



from app.models import User, Config


from app.controllers.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
from app.controllers.monitor import monitor as monitor_blueprint
monitor_blueprint.register_blueprint(auth_blueprint)
app.register_blueprint(monitor_blueprint)

