import unittest
from flask import Flask, session, g
from app import db, create_app
from app.models.user import User
from app.utils.auth import do_login, do_logout, CURR_USER_KEY
from config import TestingConfig

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.user = User(
                first_name='John',
                last_name='Doe',
                username='johndoe',
                email='john@example.com',
                password='hashed_password'
            )
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_do_login(self):
        with self.client as c:
            with self.app.test_request_context():
                user = User.query.first()
                do_login(user)
                self.assertEqual(session[CURR_USER_KEY], user.id, "User ID should be in the session after login")
                self.assertEqual(g.user, user, "g.user should be set to the logged in user")

    def test_do_logout(self):
        with self.client as c:
            with self.app.test_request_context():
                user = User.query.first()
                do_login(user)
                
                # Ensure the user ID is in the session before logout
                self.assertEqual(session[CURR_USER_KEY], user.id, "User ID should be in the session before logout.")
                self.assertEqual(g.user, user, "g.user should be set to the logged in user before logout.")
                
                do_logout()
                
                # Verify the session and g.user after logout
                self.assertNotIn(CURR_USER_KEY, session, "User ID should not be in the session after logout")
                self.assertIsNone(g.get('user'), "g.user should be None after logout")

if __name__ == '__main__':
    unittest.main()
