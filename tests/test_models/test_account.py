import unittest
from app import create_app, db
from app.models.user import User
from app.models.account import Accounts
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import TestingConfig

class TestAccountModel(unittest.TestCase):
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

            self.account1 = Accounts(
                name='John Savings',
                account_type='savings',
                balance=1000.00,
                user_id=self.user1.id,
                created_at=datetime.utcnow()
            )
            db.session.add(self.account1)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_account_creation(self):
        with self.app.app_context():
            account = Accounts.query.filter_by(name='John Savings').first()
            self.assertIsNotNone(account)
            self.assertEqual(account.balance, 1000.00)

if __name__ == '__main__':
    unittest.main()
