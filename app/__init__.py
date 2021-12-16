import celery
from flask import Flask, redirect, url_for
from flask.templating import render_template
import flask_login
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

app = Flask(__name__)


app.config.from_object('config')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager(app)

socketio = SocketIO(app)

from app.routes.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from app.routes.config import config as config_blueprint
#app.register_blueprint(config_blueprint)

from app.routes.occurrences import occurrences as occurrences_blueprint
#app.register_blueprint(occurrences_blueprint)

from app.routes.monitor import monitor as monitor_blueprint
monitor_blueprint.register_blueprint(config_blueprint)
monitor_blueprint.register_blueprint(occurrences_blueprint)

app.register_blueprint(monitor_blueprint)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('monitor.home'))
    return render_template('index.html')

