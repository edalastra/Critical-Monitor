from flask import Blueprint, render_template, Response, redirect, url_for, request, make_response, jsonify
from app import db
from flask_login import current_user
from app.models.Config import Config
from app.models.User import User
from app.models.Inference import Inference
import cv2
import base64
# from app.monitor.src.social_distanciation_video_detection import gen_frames

monitor = Blueprint('monitor', __name__)

@monitor.route('/home')
def home():
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    if len(configs) == 0:
        return redirect(url_for('monitor.config'))
    return render_template('monitor/home.html', configs=configs)

@monitor.route('/config', methods=['GET'])
def config():
    configs = Config.query.join(User.config).filter(User.id == current_user.id).all()
    return render_template('monitor/config.html', configs=configs)

@monitor.route('/register_config', methods=['POST'])
def register_config():
    try:
        content = request.json
        points = content['points']
        camera_address = content['camera_address']
        room_name =content['room_name']
        config = Config(room_name, current_user.get_id(), 2, camera_address, points, content['width'], content['height'])
        db.session.add(config)
        db.session.commit()

        return make_response(jsonify({
            "status": "Bad ok",
            }), 200)
    except Exception as e:
        return make_response(jsonify({
        "status": "Bad Request",
        "description": e
        }), 400)

@monitor.route('/access_camera', methods=['POST'])
def access_camera():
    content = request.json
    cap = cv2.VideoCapture(int(content['address']))
    if cap is None or not cap.isOpened():
        return make_response(jsonify({
            "status": "invalide input",
            "description": f"não é possivel acessar a porta {content['address']}"
        }), 400)
    
    _, frame = cap.read()
    h, w = frame.shape[:-1]
    retval, buffer = cv2.imencode('.jpg', frame)
    for i in range(2):
        _, frame = cap.read()
        retval, buffer = cv2.imencode('.jpg', frame)

    jpg_as_text = base64.b64encode(buffer).decode("utf-8")
    response = make_response(jsonify({
            "status": "ok",
            "frame": str(jpg_as_text),
            "h": h,
            "w": w
        }), 200)
    return response
   


@monitor.route('/video_feed')
def video_feed():
    config_id = request.cookies.get('camera_address')
    config = Config.query.filter(Config.id == int(config_id)).first()
    points = []
    points.append([config.point_x1, config.point_y1])
    points.append([config.point_x2, config.point_y2])
    points.append([config.point_x3, config.point_y3])
    points.append([config.point_x4, config.point_y4])

    inference = Inference(config.width_og, config.height_og, config.height_og, points)
    return Response(inference.init(), mimetype='multipart/x-mixed-replace; boundary=frame')
