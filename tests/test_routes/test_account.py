import unittest
from datetime import datetime
from flask import session
from app import create_app, db
from app.models.user import User
from app.models.account import Accounts
from werkzeug.security import generate_password_hash
from config import TestingConfig

class AccountRoutesTestCase(unittest.TestCase):
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

            self.account = Accounts(
                name="Checking Account",
                account_type="checking",
                balance=1000,
                user_id=self.user.id
            )
            db.session.add(self.account)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_account_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/account/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add an Account', response.data)

    def test_add_account_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                account = db.session.merge(self.account)
                sess['user_id'] = user.id

        response = self.client.post('/account/add', data={
            'name': 'Saving Account',
            'account_type': 'savings',
            'balance': '2000.00'
            }, follow_redirects=True)
        
        response_data = response.data.decode()
        print(response_data)

        self.assertIn('Account added successfully.', response_data)

    def test_accounts_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/account', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Accounts', response.data)

    def test_edit_account_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            account_id = db.session.merge(self.account).id

        response = self.client.get(f'/account/edit/{account_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Account', response.data)

    def test_edit_account_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            account_id = db.session.merge(self.account).id

        response = self.client.post(f'/account/edit/{account_id}', data={
            'name': 'Updated Checking Account',
            'account_type': 'checking',
            'balance': 1500
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account updated successfully.', response.data)

    def test_delete_account_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            account_id = db.session.merge(self.account).id

        response = self.client.post(f'/account/delete/{account_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account and related transactions deleted successfully.', response.data)

if __name__ == '__main__':
    unittest.main()
