import unittest
from app import create_app, db
from app.models.expense import Expense
from app.models.category import Category
from app.models.user import User
from app.models.budget import Budgets
from werkzeug.security import generate_password_hash
from datetime import datetime
from decimal import Decimal
from config import TestingConfig

class TestExpenseModel(unittest.TestCase):
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

            self.budget = Budgets(
                category_name='Groceries',
                amount=Decimal('500.00'),
                spent=Decimal('0.00'),
                start_date=datetime.now(),
                end_date=datetime.now(),
                category_id=self.category.id,
                user_id=self.user1.id
            )
            db.session.add(self.budget)
            db.session.commit()

            self.expense = Expense(
                amount=Decimal('50.00'),
                description='Grocery Shopping',
                date=datetime.now(),
                category_id=self.category.id,
                user_id=self.user1.id,
                budget_id=self.budget.id
            )
            db.session.add(self.expense)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_expense_creation(self):
        with self.app.app_context():
            expense = Expense.query.filter_by(description='Grocery Shopping').first()
            self.assertIsNotNone(expense)
            self.assertEqual(expense.amount, Decimal('50.00'))

if __name__ == '__main__':
    unittest.main()
