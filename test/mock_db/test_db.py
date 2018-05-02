import nose

from app.db import AndrewDB


def test_get_hotels():
    with nose.allure.step('Get all hotels'):
        db = AndrewDB()
        db.get_all_hotels()
