import mock
import nose

from app import app
from app.db import AndrewDB


def test_get_hotels():
    with nose.allure.step('Get all hotels'):
        with app.app_context():
            db = AndrewDB()
            expected = None
            with mock.patch('psycopg2.connect') as mock_connect:
                mock_connect.cursor.return_value.execute.fetch_all = expected
                result = db.get_all_hotels()
                assert (result == expected)
