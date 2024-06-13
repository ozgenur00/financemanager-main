import unittest
from app import app, db, add_user_to_g
from models import User, Accounts, Transactions, Budgets, Goals, Category
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from decimal import Decimal

class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the before_request handler only once."""
        app.before_request(add_user_to_g)

    def setUp(self):
        """Set up the test client and initialize the database."""
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.seed_database()

    def tearDown(self):
        """Tear down the database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_database(self):
        """Seed the database with initial data."""
        user_password = generate_password_hash('testpassword')
        user1 = User(
            first_name='John',
            last_name='Doe',
            username='unique_johndoe',
            email='unique_john@example.com',
            password=user_password,
            created_at=datetime.utcnow()
        )
        db.session.add(user1)
        db.session.commit()

        account1 = Accounts(
            name='John Savings',
            account_type='savings',
            balance=1000.00,
            user_id=user1.id,
            created_at=datetime.utcnow()
        )
        db.session.add(account1)
        db.session.commit()

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

        categories = ['Home and Utilities', 'Transportation', 'Groceries']
        for category_name in categories:
            category = Category(name=category_name)
            db.session.add(category)
        db.session.commit()

        budget1 = Budgets(
            category_name='Groceries',
            amount=Decimal('500.00'),
            spent=Decimal('0.00'),
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            category_id=Category.query.filter_by(name='Groceries').first().id,
            user_id=user1.id
        )
        db.session.add(budget1)
        db.session.commit()

        goal1 = Goals(
            name='Vacation Fund',
            target_amount=Decimal('2000.00'),
            created_at=datetime.utcnow(),
            user_id=user1.id
        )
        db.session.add(goal1)
        db.session.commit()

    def login(self):
        """Helper function to log in the test user."""
        self.client.post('/login', data=dict(
            email="unique_john@example.com",
            password="testpassword"
        ), follow_redirects=True)

    def test_signup_post(self):
        """Test the /signup route with a POST request."""
        # Initial GET request to ensure the signup page loads correctly
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signup', response.data)
    
        # Generate unique email and username for the test
        timestamp = datetime.utcnow().timestamp()
        email = f'testuser2{timestamp}@example.com'
        username = f'testuser{int(timestamp)}'[:20]  # Ensure the username is at most 20 characters long
    
        # POST request to submit the signup form
        response = self.client.post('/signup', data={
            'first_name': 'Test2',
            'last_name': 'User2',
            'username': username,
            'email': email,
            'password': 'testpassword2',
            'confirm_password': 'testpassword2'
        }, follow_redirects=True)

        # Print response data for debugging
        print("Signup response data:", response.data.decode())

        # Check if the user was created
        user = User.query.filter_by(email=email).first()
        print("User created:", user)
        self.assertIsNotNone(user, "User was not created.")

        # Ensure 'Welcome!' is present in the response
        self.assertIn(b'Welcome!', response.data)



    def test_login_post(self):
        """Test the /login route with a POST request."""
        response = self.client.post('/login', data=dict(
            email="unique_john@example.com",
            password="testpassword"
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome Back!', response.data)

    def test_logout(self):
        """Test the /logout route."""
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have successfully logged out.', response.data)

    def test_add_account(self):
        """Test adding a new account."""
        self.login()
        response = self.client.post('/account/add', data={
            'name': 'Test Account',
            'account_type': 'checking',
            'balance': 2000.00
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account added successfully.', response.data)

        account = Accounts.query.filter_by(name='Test Account').first()
        self.assertIsNotNone(account, "Account was not created.")
        self.assertEqual(account.balance, Decimal('2000.00'))

    def test_add_transaction(self):
        """Test adding a new transaction."""
        self.login()
        account = Accounts.query.filter_by(name='John Savings').first()
        category = Category.query.filter_by(name='Groceries').first()

        response = self.client.post('/transaction/add', data={
            'type': 'expense',
            'description': 'Grocery Shopping',
            'amount': '150.00',
            'date': '2023-05-01',
            'account_id': str(account.id),
            'category': str(category.id)
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction added successfully!', response.data)

        transaction = Transactions.query.filter_by(description='Grocery Shopping').first()
        self.assertIsNotNone(transaction, "Transaction was not created.")
        self.assertEqual(transaction.amount, Decimal('150.00'))

    def test_set_budget(self):
        """Test setting a new budget."""
        self.login()
        category = Category.query.filter_by(name='Groceries').first()

        response = self.client.post('/budget/set', data={
            'category': str(category.id),
            'amount': '500.00',
            'start_date': '2023-05-01',
            'end_date': '2023-06-01'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budget added.', response.data)

        budget = Budgets.query.filter_by(category_name='Groceries').first()
        self.assertIsNotNone(budget, "Budget was not created.")
        self.assertEqual(budget.amount, Decimal('500.00'))

    def test_delete_account(self):
        """Test deleting an account."""
        self.login()
        account = Accounts.query.filter_by(name='John Savings').first()
        
        # Ensure the account has transactions that need to be handled
        Transactions.query.filter_by(account_id=account.id).delete()

        response = self.client.post(f'/account/delete/{account.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account deleted successfully.', response.data)
        self.assertIsNone(Accounts.query.get(account.id))

    def test_delete_budget(self):
        """Test deleting a budget."""
        self.login()
        budget = Budgets.query.filter_by(category_name='Groceries').first()
        response = self.client.post(f'/budget/delete/{budget.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'budget deleted successfully.', response.data)
        self.assertIsNone(Budgets.query.get(budget.id))

    def test_delete_transaction(self):
        """Test deleting a transaction."""
        self.login()
        transaction = Transactions.query.filter_by(description='Supermarket shopping').first()
        response = self.client.post(f'/transaction/delete/{transaction.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction deleted successfully.', response.data)
        self.assertIsNone(Transactions.query.get(transaction.id))

    def test_accounts_page(self):
        """Test accessing the accounts page."""
        self.login()
        response = self.client.get('/account')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Accounts', response.data)

    def test_budgets_page(self):
        """Test accessing the budgets page."""
        self.login()
        response = self.client.get('/budget')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budgets', response.data)

    def test_goals_page(self):
        """Test accessing the goals page."""
        self.login()
        response = self.client.get('/goal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goals', response.data)

    def test_edit_goal(self):
        """Test editing a goal."""
        self.login()
        goal = Goals.query.filter_by(name='Vacation Fund').first()
        response = self.client.post(f'/goal/edit/{goal.id}', data={
            'name': 'New Vacation Fund',
            'target_amount': '2500.00'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goal updated successfully.', response.data)

        updated_goal = Goals.query.get(goal.id)
        self.assertEqual(updated_goal.name, 'New Vacation Fund')
        self.assertEqual(updated_goal.target_amount, Decimal('2500.00'))

    def test_edit_transaction(self):
        """Test editing a transaction."""
        self.login()
        transaction = Transactions.query.filter_by(description='Supermarket shopping').first()
        account = Accounts.query.filter_by(name='John Savings').first()
        category = Category.query.filter_by(name='Groceries').first()

        response = self.client.post(f'/transaction/edit/{transaction.id}', data={
            'account_id': str(account.id),
            'type': 'expense',
            'description': 'Supermarket shopping - edited',
            'amount': '120.00',
            'date': '2023-05-02',
            'category': str(category.id)
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transaction updated successfully.', response.data)

        updated_transaction = Transactions.query.get(transaction.id)
        self.assertEqual(updated_transaction.description, 'Supermarket shopping - edited')
        self.assertEqual(updated_transaction.amount, Decimal('120.00'))

    def test_edit_account(self):
        """Test editing an account."""
        self.login()
        account = Accounts.query.filter_by(name='John Savings').first()
        response = self.client.post(f'/account/edit/{account.id}', data={
            'name': 'John Savings - edited',
            'account_type': 'checking',
            'balance': '1200.00'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account updated successfully.', response.data)

        updated_account = Accounts.query.get(account.id)
        self.assertEqual(updated_account.name, 'John Savings - edited')
        self.assertEqual(updated_account.account_type, 'checking')
        self.assertEqual(updated_account.balance, Decimal('1200.00'))

    def test_edit_budget(self):
        """Test editing a budget."""
        self.login()
        budget = Budgets.query.filter_by(category_name='Groceries').first()
        category = Category.query.filter_by(name='Groceries').first()

        response = self.client.post(f'/budget/edit/{budget.id}', data={
            'category': str(category.id),
            'amount': '600.00',
            'start_date': '2023-05-01',
            'end_date': '2023-06-01'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Budget updated successfully.', response.data)

        updated_budget = Budgets.query.get(budget.id)
        self.assertEqual(updated_budget.amount, Decimal('600.00'))

if __name__ == '__main__':
    unittest.main()

