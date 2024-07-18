import unittest
from datetime import datetime
from flask import session
from app import create_app, db
from app.models.user import User
from app.models.budget import Budgets
from app.models.category import Category
from werkzeug.security import generate_password_hash
from config import TestingConfig

class BudgetRoutesTestCase(unittest.TestCase):
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
                username='johndoe',
                email='john@example.com',
                password=hashed_password
            )
            db.session.add(self.user)
            db.session.commit()

            self.category = Category(name="Food")
            db.session.add(self.category)
            db.session.commit()

            self.budget = Budgets(
                category_name=self.category.name,
                amount=500,
                start_date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
                end_date=datetime.strptime('2022-12-31', '%Y-%m-%d').date(),
                user_id=self.user.id,
                category_id=self.category.id
            )
            db.session.add(self.budget)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_set_budget_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/budget/set')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Set a Budget', response.data)

    def test_set_budget_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            category_id = str(db.session.merge(self.category).id)

        response = self.client.post('/budget/set', data={
            'category': category_id,
            'amount': 600,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budget added.', response.data)

    def test_budgets_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/budget', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budgets', response.data)

    def test_delete_budget_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            budget_id = db.session.merge(self.budget).id

        response = self.client.post(f'/budget/delete/{budget_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'budget deleted successfully.', response.data)

    def test_edit_budget_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            budget_id = db.session.merge(self.budget).id

        response = self.client.get(f'/budget/edit/{budget_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Budget', response.data)

    def test_edit_budget_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            budget_id = db.session.merge(self.budget).id
            category_id = str(db.session.merge(self.category).id)

        response = self.client.post(f'/budget/edit/{budget_id}', data={
            'category': category_id,
            'amount': 700,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budgets', response.data)

if __name__ == '__main__':
    unittest.main()
