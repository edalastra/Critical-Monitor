from flask import Blueprint, render_template, Response, redirect, url_for, request, make_response, jsonify
from app import db
from flask_login import current_user
from app.models.Config import Config
from app.models.User import User

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



def gen_frames(idx):
    cap = cv2.VideoCapture(idx)

    while True:	
        (frame_exists, frame) = cap.read()
        # Test if it has reached the end of the video
        if not frame_exists:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            bframe = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + bframe + b'\r\n')  # concat frame one by one and show result


@monitor.route('/register_config', methods=['POST'])
def register_config():
    try:
        content = request.json
        points = content['points']
        camera_address = content['camera_address']
        room_name =content['room_name']
        config = Config(room_name, current_user.get_id(), 2, camera_address, points)
        db.session.add(config)
        db.session.commit()

        return make_response(jsonify({
            "status": "Bad ok",
            }), 200)
    except Exception as e:
        return make_response(jsonify({
        "status": "Bad Request",
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
    response.set_cookie("camera_address", content['address'])
    return response
   


@monitor.route('/video_feed')
def video_feed():
    camera_address = request.cookies.get('camera_address')
    return Response(gen_frames(int(camera_address)), mimetype='multipart/x-mixed-replace; boundary=frame')
