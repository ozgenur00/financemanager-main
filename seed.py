import os
from sqlalchemy import inspect
from app import app, db
from app.models.user import User
from app.models.account import Accounts
from app.models.budget import Budgets
from app.models.transaction import Transactions
from app.models.goal import Goals
from app.models.category import Category
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


if os.getenv('FLASK_ENV') not in ['development', 'testing']:
    print('Seed işlemi sadece geliştirme veya test ortamında çalıştırılabilir.')
    exit()

def seed_database():
    with app.app_context():
        try:
            print(f"Database URI in seed_database: {db.engine.url}")
            db.drop_all()  
            db.create_all() 
            seed_data()  
        except Exception as e:
            print(f"An error occurred while seeding the database: {e}")

def seed_data():
    try:
        print("Seeding data...")

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

        added_user = User.query.filter_by(username='johndoe').first()
        print(f"Database check - User in seed_database: {added_user}")

        print('Database seeded!')
    except Exception as e:
        print(f"An error occurred while seeding the database: {e}")

if __name__ == '__main__':
    seed_database()
