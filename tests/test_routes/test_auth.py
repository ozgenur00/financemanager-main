import unittest
from flask import session, g
from app import db, create_app
from app.models.user import User
from app.utils.auth import CURR_USER_KEY
from werkzeug.security import generate_password_hash
from config import TestingConfig

class AuthRoutesTestCase(unittest.TestCase):
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
            db.session.refresh(self.user) 

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_success(self):
        with self.client:
            response = self.client.post('/auth/signup', data={
                'first_name': 'Jane',
                'last_name': 'Doe',
                'username': 'janedoe',
                'email': 'jane@example.com',
                'password': 'password',
                'confirm_password': 'password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Welcome!', response.data)
            with self.app.app_context():
                user = User.query.filter_by(username='janedoe').first()
                self.assertIsNotNone(user)

    def test_signup_existing_user(self):
        with self.client:
            response = self.client.post('/auth/signup', data={
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'password': 'password',
                'confirm_password': 'password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Email or username already taken', response.data)

    def test_login_success(self):
        with self.client:
            response = self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'password'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You are logged in.', response.data)
            with self.client.session_transaction() as sess:
                self.assertEqual(sess[CURR_USER_KEY], self.user.id)

    def test_login_invalid_credentials(self):
        with self.client:
            response = self.client.post('/auth/login', data={
                'email': 'john@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid email or password.', response.data)

    def test_logout(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            response = self.client.get('/auth/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You have successfully logged out.', response.data)
            with self.client.session_transaction() as sess:
                self.assertNotIn(CURR_USER_KEY, sess)

if __name__ == '__main__':
    unittest.main()
