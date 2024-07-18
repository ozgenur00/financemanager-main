from datetime import datetime
from . import db

class Goals(db.Model):
    """Goals model"""
    __tablename__ = 'goals'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    target_amount = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)