from datetime import datetime
from . import db

class Budgets(db.Model):
    """Budgets model"""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)

    spent = db.Column(db.Numeric(10,2), nullable=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref='budgets')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"<Budget id={self.id}, category_name={self.category_name}, amount={self.amount}, start_date={self.start_date}, end_date={self.end_date}, created_at={self.created_at}>"