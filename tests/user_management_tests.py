import unittest
import json

from app import create_app
from config import Config

class TEST_CONFIG(Config):
    TESTING = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


class UserManagementTestCases(unittest.TestCase):
    def setUp(self):
        app = create_app(TEST_CONFIG)
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_implemetation(self):
        self.assertEqual(200, 200)


if __name__ == '__main__':
    unittest.main()
