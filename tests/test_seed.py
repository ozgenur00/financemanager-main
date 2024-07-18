import unittest
from app import create_app, db
from app.models.user import User
from app.models.account import Accounts
from app.models.transaction import Transactions
from app.models.category import Category
from app.models.budget import Budgets
from app.models.goal import Goals
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from config import TestingConfig

class TestDatabaseSeeding(unittest.TestCase):

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        print("Tablolar oluşturuldu")
        print(f"Database URI in setUp: {db.engine.url}")
        self.seed_database()  # Seed the database during setup
        db.session.commit()  # Commit any outstanding transactions
        db.session.remove()  # Ensure session is properly closed

    def tearDown(self):
        """Tear down the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_database(self):
        print(f"Database URI in seed_database: {db.engine.url}")
        try:
            categories = [
                'Home and Utilities', 'Transportation', 'Groceries',
                'Health', 'Restaurants and Dining', 'Shopping and Entertainment',
                'Cash and Checks', 'Business Expenses', 'Education', 'Finance'
            ]

            for category_name in categories:
                category = Category(name=category_name)
                db.session.add(category)
            db.session.commit()
            print("Categories added")

            user1 = User(
                first_name='John',
                last_name='Doe',
                username='johndoe',
                email='john@example.com',
                password=generate_password_hash('your_plain_text_password')
            )
            db.session.add(user1)
            db.session.commit()
            print(f"Added user: {user1}")

            account1 = Accounts(
                name='John Savings',
                account_type='savings',
                balance=1000.00,
                user_id=user1.id
            )
            db.session.add(account1)
            db.session.commit()
            print(f"Added account: {account1}")

            transaction1 = Transactions(
                type='expense',
                description='Supermarket shopping',
                amount=100,
                date=datetime.now(),
                account_id=account1.id,
                user_id=user1.id
            )
            db.session.add(transaction1)
            db.session.commit()
            print(f"Added transaction: {transaction1}")

            budget1 = Budgets(
                category_name='Groceries',
                amount=500,
                spent=0,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                category_id=Category.query.filter_by(name='Groceries').first().id,
                user_id=user1.id
            )
            db.session.add(budget1)
            db.session.commit()
            print(f"Added budget: {budget1}")

            goal1 = Goals(
                name='Vacation Fund',
                target_amount=2000,
                created_at=datetime.now() + timedelta(days=365),
                user_id=user1.id
            )
            db.session.add(goal1)
            db.session.commit()
            print(f"Added goal: {goal1}")

            # Ek kontrol: Veritabanındaki kullanıcıyı kontrol et
            added_user = User.query.filter_by(username='johndoe').first()
            print(f"Database check - User in seed_database: {added_user}")

            print('Database seeded!')
        except Exception as e:
            print(f"An error occurred while seeding the database: {e}")

    def test_database_seeding(self):
        """Test the database seeding functionality."""
        with self.app.app_context():
            print(f"Test Database URI: {db.engine.url}")

            # Verify the seeded data
            user = User.query.filter_by(username='johndoe').first()
            print(f"Test check - User: {user}")

            # Ek hata ayıklama: Veritabanındaki tüm kullanıcıları kontrol et
            all_users = User.query.all()
            print(f"All Users: {all_users}")

            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'john@example.com')

            account = Accounts.query.filter_by(name='John Savings').first()
            print(f"Account: {account}")
            self.assertIsNotNone(account)
            self.assertEqual(account.balance, 1000.00)
            self.assertEqual(account.user_id, user.id)

            transaction = Transactions.query.filter_by(description='Supermarket shopping').first()
            print(f"Transaction: {transaction}")
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction.amount, 100)
            self.assertEqual(transaction.account_id, account.id)
            self.assertEqual(transaction.user_id, user.id)

            categories = Category.query.all()
            category_names = [category.name for category in categories]
            expected_categories = [
                'Home and Utilities', 'Transportation', 'Groceries',
                'Health', 'Restaurants and Dining', 'Shopping and Entertainment',
                'Cash and Checks', 'Business Expenses', 'Education', 'Finance'
            ]
            print(f"Categories: {category_names}")
            self.assertEqual(sorted(category_names), sorted(expected_categories))

            budget = Budgets.query.filter_by(category_name='Groceries').first()
            print(f"Budget: {budget}")
            self.assertIsNotNone(budget)
            self.assertEqual(budget.amount, 500)
            self.assertEqual(budget.user_id, user.id)

            goal = Goals.query.filter_by(name='Vacation Fund').first()
            print(f"Goal: {goal}")
            self.assertIsNotNone(goal)
            self.assertEqual(goal.target_amount, 2000)
            self.assertEqual(goal.user_id, user.id)

if __name__ == '__main__':
    unittest.main()
