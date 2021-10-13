from flask import Blueprint, render_template, Response, redirect, url_for
from flask_login import current_user
from app.models.Forms import ConfigForm
from app.models.User import User
import cv2
from app.monitor.src.social_distanciation_video_detection import gen_frames

monitor = Blueprint('monitor', __name__)

@monitor.route('/home')
def home():
    user = current_user
    print(current_user.has_config)

    if not current_user.has_config:
        return redirect(url_for('monitor.config'))
    return render_template('monitor/home.html')

@monitor.route('/config')
def config():
    form = ConfigForm()
    if form.validate_on_submit():
        print(form.minimum_distance.data)

    return render_template('monitor/config.html', form=form)


@monitor.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
