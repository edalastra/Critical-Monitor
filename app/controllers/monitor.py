from flask import Blueprint, render_template

monitor = Blueprint('monitor', __name__)

@monitor.route('/home')
def home():
    return render_template('monitor/home.html')