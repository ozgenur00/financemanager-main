from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

from app.models.expense import Expense
from app.models.category import Category
from app.models.user import User
from app.models.account import Accounts
from app.models.budget import Budgets
from app.models.transaction import Transactions
from app.models.goal import Goals

__all__ = ['Expense', 'Category', 'User', 'Accounts', 'Budgets', 'Transactions', 'Goals']


def connect_db(app):
    """Connect this database to provided Flask app."""
    db.app = app
    db.init_app(app)
