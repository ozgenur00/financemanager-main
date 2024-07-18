import unittest
from datetime import datetime
from flask import session
from app import create_app, db
from app.models.user import User
from app.models.goal import Goals
from werkzeug.security import generate_password_hash
from config import TestingConfig

class GoalRoutesTestCase(unittest.TestCase):
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

            self.goal = Goals(
                name="Save for vacation",
                target_amount=1000,
                user_id=self.user.id
            )
            db.session.add(self.goal)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_set_goal_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/goal/set')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Set a Goal', response.data)

    def test_set_goal_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.post('/goal/set', data={
            'name': 'Save for new car',
            'target_amount': 5000
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goal added.', response.data)

    def test_goals_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        response = self.client.get('/goal', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goals', response.data)

    def test_edit_goal_route_get(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            goal_id = db.session.merge(self.goal).id

        response = self.client.get(f'/goal/edit/{goal_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Goal', response.data)

    def test_edit_goal_route_post(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            goal_id = db.session.merge(self.goal).id

        response = self.client.post(f'/goal/edit/{goal_id}', data={
            'name': 'Save for vacation updated',
            'target_amount': 2000
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goal updated successfully.', response.data)

    def test_delete_goal_route(self):
        with self.client.session_transaction() as sess:
            with self.app.app_context():
                user = db.session.merge(self.user)
                sess['user_id'] = user.id

        with self.app.app_context():
            goal_id = db.session.merge(self.goal).id

        response = self.client.post(f'/goal/delete/{goal_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Goal deleted successfully.', response.data)

if __name__ == '__main__':
    unittest.main()
