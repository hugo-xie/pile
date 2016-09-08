import os
import unittest
from application.default_settings import _basedir
from application import app, db

class ManagerTestCase(unittest.TestCase):
    """ setup and teardown for the testing database """

    def setUp(self):
        create_db_dir = _basedir + '/db'
        if not os.path.exists(create_db_dir):
            os.mkdir(create_db_dir, 0o755)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'
                                    + os.path.join(_basedir, 'db/tests.db'))
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class OriginalRoutes(ManagerTestCase):
    """ test suite for the original in app routes """

    def route_username(self, username):
        return self.app.get('/hello/%s' % (username), follow_redirects=True)

    def test_username(self):
        rv = self.route_username('alberto')
        self.assertEqual('Hello, alberto!', rv.data)

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual('Hello, world!', rv.data)
