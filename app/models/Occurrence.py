from app import db
from sqlalchemy.sql import func
from sqlalchemy import CheckConstraint


class Occurrence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    occurrence_type = db.Column(db.String(15), CheckConstraint("occurrence_type IN (lotação, distânciamento)"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    amount_of_people = db.Column(db.Integer, CheckConstraint("amount_of_people >= 0"), nullable=False)
    config_id = db.Column(db.Integer, db.ForeignKey('config.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, occurrence_type, amount_of_people, config_id):
        self.occurrence_type = occurrence_type
        self.amount_of_people = amount_of_people
        self.config_id = config_id
        self.timestamp = func.now()
