from app.models.Config import Config
from flask_login import current_user
from app import db
import base64
import cv2

def new_config(content):
    points = content['points']
    camera_address = content['camera_address']
    room_name =content['room_name']
    width = content['width']
    height = content['height']
    size_frame = content['size_frame']
    capacity = content['capacity']

    config = Config(room_name, current_user.get_id(), 100, camera_address, points, width, height, size_frame, capacity)
    db.session.add(config)
    db.session.commit()

    return config

def get_snapshot(content):
    video_source = None
    
    try:
        video_source = int(content['address'])
    except ValueError:
        video_source = content['address']

    cap = cv2.VideoCapture(video_source)
    if cap is None or not cap.isOpened():
        raise Exception('Invalid video source')
    _, frame = cap.read()
    h, w = frame.shape[:2]
    retval, buffer = cv2.imencode('.jpg', frame)
    for i in range(2):
        _, frame = cap.read()
        retval, buffer = cv2.imencode('.jpg', frame)

    jpg_as_text = base64.b64encode(buffer).decode("utf-8")
    return {
            "status": "ok",
            "frame": str(jpg_as_text),
            "h": h,
            "w": w}