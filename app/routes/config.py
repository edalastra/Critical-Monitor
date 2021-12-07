from flask import Blueprint, render_template, Response, redirect, url_for, request, make_response, jsonify
from app import db
from flask_login import  current_user
from app.models.Config import Config
from app.controllers.monitor_controller import new_config, get_snapshot
from app.models.User import User


config = Blueprint('config', __name__)

@config.route('/config/<int:config_id>', methods=['GET'])
def config_get(config_id):
    config = Config.query.filter(Config.id == config_id).first()        
    c = {"id": config.id, "room_name": config.room_name, "minimun_distance": config.minimum_distance, "capacity": config.capacity}
    return make_response(jsonify(c), 200)

@config.route('/register_config', methods=['POST'])
def register_config():
    try:
        content = request.json
        new_config(content)
        return make_response(jsonify({
            "status": "ok"}), 200)
    except Exception as e:
        return make_response(jsonify({
        "status": "Bad Request",
        "description": e
        }), 400)

@config.route('/access_camera', methods=['POST'])
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

@config.route('/delete_config/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    config = Config.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    return redirect(url_for('monitor.config'))

@config.route('/config/<int:config_id>/alter_attr', methods=['PUT'])
def alter_capacity(config_id):
    attr = request.args.get('attr')
    content = request.json
    config = Config.query.get_or_404(config_id)
    if attr == 'capacity':
        config.capacity = content['capacity']
    elif attr == 'minimum_distance':
        config.minimum_distance = content['minimum_distance']
    db.session.commit()
    return make_response(jsonify({
        "status": "ok"}), 200)