from datetime import datetime
from . import db

class Transactions(db.Model):
    """Transactions model"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    type = db.Column(db.Text)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10,2))
    date = db.Column(db.Date)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref='transactions')

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='transactions')

