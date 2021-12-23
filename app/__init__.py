''' app config file '''
from flask import Flask, redirect, url_for, flash
from flask.templating import render_template
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

from app.routes import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from app.routes import config as config_blueprint
#app.register_blueprint(config_blueprint)

from app.routes import occurrences as occurrences_blueprint
#app.register_blueprint(occurrences_blueprint)

from app.routes import monitor as monitor_blueprint
monitor_blueprint.register_blueprint(config_blueprint)
monitor_blueprint.register_blueprint(occurrences_blueprint)

app.register_blueprint(monitor_blueprint)

@app.route('/')
def index():
    ''' index page '''
    if current_user.is_authenticated:
        return redirect(url_for('monitor.home'))
    return render_template('index.html')

@app.errorhandler(500)
def internal_error(error):
    flash("Ocorreu um erro interno. Por favor, tente novamente mais tarde.", "error")
