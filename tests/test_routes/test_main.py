import unittest
from flask import g, session
from app import create_app, db
from app.models.user import User
from app.models.account import Accounts
from app.models.transaction import Transactions
from app.models.budget import Budgets
from app.models.goal import Goals
from app.models.category import Category 
from werkzeug.security import generate_password_hash
from config import TestingConfig
from datetime import datetime

class MainRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            hashed_password = generate_password_hash('password')
            self.user = User(
                first_name='John',
                last_name='Doe',
                username='johndoetest', 
                email='johntest@example.com',
                password=hashed_password
            )
            db.session.add(self.user)
            db.session.commit()

            self.category = Category(name="Food")
            db.session.add(self.category)
            db.session.commit()

            self.account = Accounts(user_id=self.user.id, name="Checking", account_type="checking", balance=1000)
            db.session.add(self.account)
            db.session.commit()

            self.transaction = Transactions(user_id=self.user.id, account_id=self.account.id, amount=100, date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(), type="income")
            db.session.add(self.transaction)
            db.session.commit()

            self.budget = Budgets(user_id=self.user.id, category_name="Food", amount=500, spent=250, category_id=self.category.id)
            db.session.add(self.budget)
            db.session.commit()

            self.goal = Goals(user_id=self.user.id, name="Save for vacation", target_amount=1000)
            db.session.add(self.goal)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wealth Watcher', response.data) 

    def test_after_login_route_logged_in(self):
        with self.client:
            with self.client.session_transaction() as sess:
                with self.app.app_context():
                    self.user = db.session.merge(self.user) 
                    sess['user_id'] = self.user.id
            response = self.client.get('/main-page')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'id="accountsChart"', response.data)  
            self.assertIn(b'Welcome, John', response.data)

if __name__ == '__main__':
    unittest.main()
