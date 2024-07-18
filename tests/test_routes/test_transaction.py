import unittest
from datetime import datetime
from flask import session
from decimal import Decimal
from app import create_app, db
from app.models.user import User
from app.models.account import Accounts
from app.models.category import Category
from app.models.transaction import Transactions
from werkzeug.security import generate_password_hash
from config import TestingConfig

class TransactionRoutesTestCase(unittest.TestCase):
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

            self.category = Category(
                name="Groceries"
            )
            db.session.add(self.category)
            db.session.commit()

            self.transaction = Transactions(
                type="expense",
                description="Grocery shopping",
                amount=Decimal('100.00'),
                date=datetime.now().date(),
                account_id=self.account.id,
                user_id=self.user.id,
                category_id=self.category.id
            )
            db.session.add(self.transaction)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_transaction_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/transaction/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a Transaction', response.data)

    def test_add_transaction_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                account = db.session.merge(self.account)
                sess['user_id'] = user.id

        response = self.client.post('/transaction/add', data={
            'type': 'income',
            'description': 'Salary',
            'amount': '5000.00',
            'date': '2024-07-01',
            'account_id': str(account.id),
            'category': ''
        }, follow_redirects=True)

        # Print response data to debug
        response_data = response.data.decode()
        print(response_data)

        # Check if flash message is in response data
        self.assertIn('Transaction added successfully!', response_data)


    def test_add_expense_transaction_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                account = db.session.merge(self.account)
                category = db.session.merge(self.category)
                sess['user_id'] = user.id

        response = self.client.post('/transaction/add', data={
            'type': 'expense',
            'description': 'Groceries',
            'amount': '100.00',
            'date': '2024-07-01',
            'account_id': str(account.id),
            'category': str(category.id)
        }, follow_redirects=True)
    
        print(response.data.decode())  # Print response data to debug

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction added successfully!', response.data)


    def test_transactions_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/transaction', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transactions', response.data)

    def test_edit_transaction_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            transaction_id = db.session.merge(self.transaction).id

        response = self.client.get(f'/transaction/edit/{transaction_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Transaction', response.data)

    def test_edit_transaction_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                transaction = db.session.merge(self.transaction)
                account = db.session.merge(self.account)
                category = db.session.merge(self.category)
                sess['user_id'] = user.id

        response = self.client.post(f'/transaction/edit/{transaction.id}', data={
            'type': 'expense',
            'description': 'Updated Grocery shopping',
            'amount': '150.00',
            'date': '2024-07-01',
            'account_id': str(account.id),
            'category': str(category.id)
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction updated successfully.', response.data)

    def test_delete_transaction_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                transaction = db.session.merge(self.transaction)
                sess['user_id'] = user.id

        response = self.client.post(f'/transaction/delete/{transaction.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction deleted successfully.', response.data)

if __name__ == '__main__':
    unittest.main()
