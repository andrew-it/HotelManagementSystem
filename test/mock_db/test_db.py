import mock
import nose

from app.db import AndrewDB


@mock.patch("psycopg2.connect")
@mock.patch("psycopg2.extensions.cursor.fetchall")
def test_get_hotels():
    with nose.allure.step('Get all hotels'):
        db = AndrewDB()
        query_result = None
        with mock.patch('psycopg2.connect') as mock_connect:
            mock_connect.cursor.return_value.execute.fetch_all = query_result
            db.get_all_hotels()