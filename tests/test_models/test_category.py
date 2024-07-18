import unittest
from app import create_app, db
from app.models.category import Category
from config import TestingConfig

class TestCategoryModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        with self.app.app_context():
            db.create_all()

            self.category = Category(name='Groceries')
            db.session.add(self.category)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_category_creation(self):
        with self.app.app_context():
            category = Category.query.filter_by(name='Groceries').first()
            self.assertIsNotNone(category)
            self.assertEqual(category.name, 'Groceries')

if __name__ == '__main__':
    unittest.main()
