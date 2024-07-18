from datetime import datetime
from . import db

class Expense(db.Model):
    """Expense model"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.today())

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref='expenses')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='expenses')

    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    budget = db.relationship('Budgets', backref='expenses')

    def __repr__(self):
        return f"<Expense id={self.id}, amount={self.amount}, description={self.description}, date={self.date}>"
