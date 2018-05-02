import allure
import mock

from app import app
from app.db import AndrewDB


@mock.patch("psycopg2.connect")
def test_get_hotels(mock_connect):
    with allure.step('Get all hotels'):
        with app.app_context():
            db = AndrewDB()
            expected = ['hotel1']
            mock_connect().cursor.return_value.fetchone.return_value.__getitem__('hotels').return_value = expected
            result = db.get_all_hotels().return_value
        assert result == expected


@mock.patch("psycopg2.connect")
def test_get_admins(mock_connect):
    with allure.step('Get all hotels'):
        with app.app_context():
            db = AndrewDB()
            expected = ['admin1', 'admin2']
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_all_admins()
        assert result == expected
