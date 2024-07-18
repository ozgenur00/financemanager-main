from datetime import datetime
from . import db

class Accounts(db.Model):
    """Accounts model"""
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text)
    account_type = db.Column(db.Text)
    balance = db.Column(db.Numeric(10,2))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transactions = db.relationship('Transactions', backref='account', lazy=True, cascade="all, delete-orphan")

