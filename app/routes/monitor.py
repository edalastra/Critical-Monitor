''' monitor template routes '''
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, Response, redirect, url_for, request, make_response, jsonify
from flask_login import current_user, login_required
from app.models import Config
from app.models import User
from app.models import Inference
from app.models import Occurrence
from app.controllers.monitor_controller import new_config, get_snapshot
from app.utils import datetime_range

monitor = Blueprint('monitor', __name__)

@monitor.route('/home')
@login_required
def home():
    ''' home page '''
    configs = Config.query.with_entities(Config.id, Config.room_name).join(User.config).filter(User.id == current_user.id).all()
    if len(configs) == 0:
        return redirect(url_for('monitor.config'))
    return render_template('monitor/home.html', configs=configs)

@monitor.route('/config', methods=['GET'])
@login_required
def config():
    ''' config page '''
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    return render_template('monitor/config.html', configs=configs)

@monitor.route('/video_feed')
@login_required
def video_feed():
    ''' video feed '''
    config_id = request.cookies.get('camera_address')
    config = Config.query.filter(Config.id == int(config_id)).first()
    points = []
    points.append([config.point_x4, config.point_y4])
    points.append([config.point_x1, config.point_y1])
    points.append([config.point_x3, config.point_y3])
    points.append([config.point_x2, config.point_y2])
    inference = Inference(config.id, config.width_og, config.height_og, config.size_frame, points, config.capacity, config.camera_address, config.minimum_distance)
    return Response(inference.init(), mimetype='multipart/x-mixed-replace; boundary=frame')

@monitor.route('/occurrences', methods=['GET'])
@login_required
def occurrences():
    ''' occurrences page '''
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    return render_template('monitor/occurrences_per_date.html', configs=configs)

@monitor.route('/occurrences/<int:config_id>/<int:occ_date>', methods=['GET'])
def list_occurrences(config_id, occ_date):
    ''' list occurrences per date '''
    occ_date = datetime.fromtimestamp(occ_date)
    min_date = datetime(occ_date.year, occ_date.month, occ_date.day , 0, 0)
    max_date = datetime(occ_date.year, occ_date.month, occ_date.day , 23, 59, 59)
    occurrences = Occurrence.query.filter(
        Occurrence.config_id == config_id and (Occurrence.timestamp >= min_date and Occurrence.timestamp <= max_date)
    ).order_by(Occurrence.timestamp.desc()).all()
    dts = [dt for dt in 
       datetime_range(
       datetime(occ_date.year, occ_date.month, occ_date.day + 1 , 0, 0), 
       datetime(occ_date.year, occ_date.month, occ_date.day + 1, 23, 59, 59),#datetime(2016, 9, 1, 9+12), 
       timedelta(minutes=30))]
    data = []
    for i in range(0,len(dts) - 1):
        count = 0
        for occ in occurrences:
            if dts[i] <= occ.timestamp and dts[i+1] >= occ.timestamp:
                count += 1
        data.append(count)

    labels = list(map(lambda x: x.strftime("%H:%M"), dts)) 

    return render_template('monitor/occurrences.html', occurrences=occurrences, occurrences_json=json.dumps({"x": labels, "y": data }, ensure_ascii=False))
