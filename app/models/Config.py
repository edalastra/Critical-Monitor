''' SqlAlchemy ORM model for the Config table '''
from typing import List
from app import db

class Config(db.Model):
    ''' Config table '''

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    minimum_distance = db.Column(db.Integer, nullable=False)
    camera_address = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    point_x1 = db.Column(db.Integer)
    point_y1 = db.Column(db.Integer)
    point_x2 = db.Column(db.Integer)
    point_y2 = db.Column(db.Integer)
    point_x3 = db.Column(db.Integer)
    point_y3 = db.Column(db.Integer)
    point_x4 = db.Column(db.Integer)
    point_y4 = db.Column(db.Integer)
    size_frame = db.Column(db.Integer)
    width_og= db.Column(db.Integer)
    height_og = db.Column(db.Integer)
    occurrences = db.relationship('Occurrence', backref='config', lazy=True, passive_deletes=True)

    def __init__(self, room_name: str,
                user_id: int, minimum_distance: int,
                camera_address: str,
                points: List,
                width_og: int,
                height_og: int,
                size_frame: int,
                capacity: int
                ) -> None:
        self.room_name = room_name
        self.user_id = user_id
        self.minimum_distance = minimum_distance
        self.camera_address = camera_address
        self.point_x1 = points[0][0]
        self.point_y1 = points[0][1]
        self.point_x2 = points[1][0]
        self.point_y2 = points[1][1]
        self.point_x3 = points[2][0]
        self.point_y3 = points[2][1]
        self.point_x4 = points[3][0]
        self.point_y4 = points[3][1]
        self.width_og = width_og
        self.height_og = height_og
        self.size_frame = size_frame
        self.capacity = capacity
