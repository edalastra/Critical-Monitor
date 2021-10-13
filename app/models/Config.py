from app import db

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    minimum_distance = db.Column(db.Integer, nullable=False)
    camera_address = db.Column(db.String, nullable=False)

    def __init__(self, user_id, minimum_distance, camera_address):
        self.user_id = user_id
        self.minimum_distance = minimum_distance
        self.camera_address = camera_address 