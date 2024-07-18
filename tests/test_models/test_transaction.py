import unittest
from app import create_app, db
from app.models.transaction import Transactions
from app.models.category import Category
from app.models.user import User
from app.models.account import Accounts
from werkzeug.security import generate_password_hash
from datetime import datetime
from decimal import Decimal
from config import TestingConfig

class TestTransactionModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        with self.app.app_context():
            db.create_all()

            user_password = generate_password_hash('testpassword')
            self.user1 = User(
                first_name='John',
                last_name='Doe',
                username='unique_johndoe',
                email='unique_john@example.com',
                password=user_password,
                created_at=datetime.utcnow()
            )
            db.session.add(self.user1)
            db.session.commit()

            self.category = Category(name='Groceries')
            db.session.add(self.category)
            db.session.commit()

            self.account = Accounts(
                name='John Savings',
                account_type='savings',
                balance=1000.00,
                user_id=self.user1.id,
                created_at=datetime.utcnow()
            )
            db.session.add(self.account)
            db.session.commit()

            self.transaction = Transactions(
                type='expense',
                description='Grocery Shopping',
                amount=Decimal('100.00'),
                date=datetime.now(),
                category_id=self.category.id,
                account_id=self.account.id,
                user_id=self.user1.id
            )
            db.session.add(self.transaction)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_transaction_creation(self):
        with self.app.app_context():
            transaction = Transactions.query.filter_by(description='Grocery Shopping').first()
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction.amount, Decimal('100.00'))

if __name__ == '__main__':
    unittest.main()
