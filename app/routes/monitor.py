from datetime import time
from flask import Blueprint, render_template, Response, redirect, url_for, request, make_response, jsonify
from flask.helpers import flash
from sqlalchemy.sql.expression import label
from app import db
from flask_login import current_user, login_required
from functools import reduce
from sqlalchemy import and_

from app.models.Config import Config
from app.models.User import User
from app.models.Inference import Inference
from app.models.Occurrence import Occurrence
from app.controllers.monitor_controller import new_config, get_snapshot
from app.utils import datetime_range
import sqlalchemy as sa
import json
from datetime import datetime, timedelta
import numpy as np

# from app.monitor.src.social_distanciation_video_detection import gen_frames

monitor = Blueprint('monitor', __name__)


@monitor.route('/home')
@login_required
def home():
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    if len(configs) == 0:
        return redirect(url_for('monitor.config'))
    return render_template('monitor/home.html', configs=configs)

@monitor.route('/config', methods=['GET'])
@login_required
def config():
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    return render_template('monitor/config.html', configs=configs)

@monitor.route('/register_config', methods=['POST'])
def register_config():
    try:
        content = request.json
        config = new_config(content)
        return make_response(jsonify({
            "status": "ok"}), 200)
    except Exception as e:
        return make_response(jsonify({
        "status": "Bad Request",
        "description": e
        }), 400)

@monitor.route('/access_camera', methods=['POST'])
def access_camera():
    content = request.json
    try:
        image = get_snapshot(content)
        return make_response(jsonify(image), 200)
    except Exception as e:
        return make_response(jsonify({
        "status": "Bad Request",
        "description": e
        }), 400)

@monitor.route('/delete_config/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    config = Config.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()

    return redirect(url_for('monitor.config'))

@monitor.route('/video_feed')
def video_feed():
    config_id = request.cookies.get('camera_address')
    config = Config.query.filter(Config.id == int(config_id)).first()
    points = []
    points.append([config.point_x4, config.point_y4])
    points.append([config.point_x1, config.point_y1])
    points.append([config.point_x3, config.point_y3])
    points.append([config.point_x2, config.point_y2])

    inference = Inference(config.id, config.width_og, config.height_og, config.size_frame, points, config.capacity, config.camera_address)

    return Response(inference.init(), mimetype='multipart/x-mixed-replace; boundary=frame')


@monitor.route('/occurrences', methods=['GET'])
@login_required
def occurrences():
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    return render_template('monitor/occurrences_per_date.html', configs=configs)

@monitor.route('/occurrences/<int:config_id>', methods=['GET'])
def occurrences_per_day(config_id):
    # configs = db.session\
    #     .query(Occurrence.timestamp, sa.func.count(Occurrence.id).label('q_occurrences'))\
    #     .join(Config.occurrences)\
    #     .filter(Config.id == config_id)\
    #     .group_by(Occurrence.timestamp).all()
    sql = """SELECT 
	COUNT(CASE WHEN oc.occurrence_type = 'lotação' THEN 1 END) as capacity,
	COUNT(CASE WHEN oc.occurrence_type = 'distânciamento' THEN 1 END) as distancing,
	DATE(oc.timestamp) as occurrence_date
	FROM occurrence oc
		JOIN config co ON co.id = oc.config_id
		JOIN "user" u ON u.id = co.user_id
	WHERE co.id = :c_id AND u.id = :u_id
	    GROUP BY occurrence_date
	    ORDER BY occurrence_date DESC;"""
    
    result = db.session.execute(sql,  {"u_id": current_user.id, "c_id": config_id})
    occurrences_per_date = []
    for r in result:
        occurrences_per_date.append({
            "capacity_qtd": r[0],
            "distancing_qtd": r[1],
            "occurrency_date": r[2]
        })
    return  make_response(jsonify({"dates":occurrences_per_date}), 200)

@monitor.route('/occurrences/<int:config_id>/<int:occ_date>', methods=['GET'])
def list_occurrences(config_id, occ_date):
    occ_date = datetime.fromtimestamp(occ_date)
    min_date = datetime(occ_date.year, occ_date.month, occ_date.day , 0, 0)
    max_date = datetime(occ_date.year, occ_date.month, occ_date.day , 23, 59, 59)

    occurrences = Occurrence.query.filter(
        Occurrence.config_id == config_id and (Occurrence.timestamp >= min_date and Occurrence.timestamp <= max_date)
    ).order_by(Occurrence.timestamp.desc()).all()
    
    # min_ts =  min(occ_dts)
    # max_ts =  max(occ_dts)

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
        #print(count)
        data.append(count)

        
    # for row in occurrences:
    #     if row.type == "lotação":
    #         {
    #             "amount_people": row.amount_of_people,
    #             "timestamp": datetime.timestamp(row.timestamp),
    #             "type": str(row.occurrence_type)
    #         }

    occurrences_json = [{
        "amount_people": row.amount_of_people,
        "timestamp": datetime.timestamp(row.timestamp),
        "type": str(row.occurrence_type)
        } for row in occurrences]

    labels = list(map(lambda x: x.strftime("%H:%M"), dts)) 

    return render_template('monitor/occurrences.html', occurrences=occurrences, occurrences_json=json.dumps({"x": labels, "y": data }, ensure_ascii=False))