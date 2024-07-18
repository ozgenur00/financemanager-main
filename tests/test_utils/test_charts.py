import unittest
from flask import Flask, session, g
from app import db, create_app
from app.models.user import User
from app.models.budget import Budgets
from app.models.account import Accounts
from app.models.transaction import Transactions
from app.models.category import Category
from app.utils.charts import create_budget_vs_spent_chart, create_account_balance_chart, generate_accounts_balance_chart, generate_financials_chart
from config import TestingConfig
from datetime import datetime

class ChartsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.user = User(
                first_name='John',
                last_name='Doe',
                username='johndoe',
                email='john@example.com',
                password='hashed_password'
            )
            db.session.add(self.user)
            db.session.commit()

            # Create default categories and accounts for tests
            self.category = Category(name='Food')
            db.session.add(self.category)
            db.session.commit()

            self.account = Accounts(user_id=self.user.id, name="Default Account", account_type="checking", balance=1000)
            db.session.add(self.account)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_budget_vs_spent_chart(self):
        with self.app.app_context():
            user = User.query.filter_by(username='johndoe').first()
            category = Category.query.filter_by(name='Food').first()
            budget = Budgets(user_id=user.id, category_name="Food", amount=500, spent=250, category_id=category.id)
            db.session.add(budget)
            db.session.commit()

            chart_div = create_budget_vs_spent_chart(user.id)
            self.assertIn('<div id=', chart_div, "The chart div should be in the output")

    def test_create_account_balance_chart(self):
        with self.app.app_context():
            user = User.query.filter_by(username='johndoe').first()
            account = Accounts.query.filter_by(name="Default Account").first()

            transaction1 = Transactions(user_id=user.id, account_id=account.id, date=datetime.strptime('2024-01-01', '%Y-%m-%d').date(), amount=100)
            transaction2 = Transactions(user_id=user.id, account_id=account.id, date=datetime.strptime('2024-01-01', '%Y-%m-%d').date(), amount=-50)
            db.session.add(transaction1)
            db.session.add(transaction2)
            db.session.commit()

            chart_div = create_account_balance_chart(user.id)
            self.assertIn('<div id=', chart_div, "The chart div should be in the output")

    def test_generate_accounts_balance_chart(self):
        with self.app.app_context():
            user = User.query.filter_by(username='johndoe').first()
            account1 = Accounts(user_id=user.id, name="Checking", account_type="checking", balance=1000)
            account2 = Accounts(user_id=user.id, name="Savings", account_type="savings", balance=2000)
            db.session.add(account1)
            db.session.add(account2)
            db.session.commit()

            chart_div = generate_accounts_balance_chart(user.id)
            self.assertIn('<div id=', chart_div, "The chart div should be in the output")

    def test_generate_financials_chart(self):
        with self.app.app_context():
            user = User.query.filter_by(username='johndoe').first()
            account = Accounts.query.filter_by(name="Default Account").first()

            transaction1 = Transactions(user_id=user.id, type='income', date=datetime.strptime('2024-01-01', '%Y-%m-%d').date(), amount=1000, account_id=account.id)
            transaction2 = Transactions(user_id=user.id, type='expense', date=datetime.strptime('2024-01-01', '%Y-%m-%d').date(), amount=-500, account_id=account.id)
            db.session.add(transaction1)
            db.session.add(transaction2)
            db.session.commit()

            chart_div = generate_financials_chart(user.id)
            self.assertIn('<div id=', chart_div, "The chart div should be in the output")

if __name__ == '__main__':
    unittest.main()
