from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from . import db
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()


class User(db.Model):
    """Users model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    accounts = db.relationship('Accounts', backref='user', lazy=True)
    budgets = db.relationship('Budgets', backref='user', lazy=True)
    goals = db.relationship('Goals', backref='user', lazy=True)

    @staticmethod
    def authentication(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None


    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        hashed_pwd = generate_password_hash(password)
        user = cls(first_name=first_name, last_name=last_name, username=username, email=email, password=hashed_pwd)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            print(f"IntegrityError during signup: {e.orig}")
            db.session.rollback()
            return None
        except Exception as e:
            print(f"Exception during signup: {e}")
            db.session.rollback()
            return None
        return user
    
    def check_password(self, password):
        return check_password_hash(self.password, password)