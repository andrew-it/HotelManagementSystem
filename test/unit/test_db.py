import allure
import mock

from app import app
from app.db import AndrewDB, searchOp


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_sys_user_get_id(mock_connect):
    with allure.step('Insert into sys_user and get id'):
        with app.app_context():
            db = AndrewDB()
            expected = {'user_id': 5}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.insert_sys_user_get_id("email@example.com", "123456")
        assert result == expected['user_id']


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_sys_user(mock_connect):
    with allure.step('Insert into sys_user and get user'):
        with app.app_context():
            db = AndrewDB()
            expected = {'user_id': 5, 'email': "email@example.com", 'password': "123456", 'role': "ROLE_ADMIN"}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.insert_sys_user("email@example.com", "123456")
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_admin(mock_connect):
    with allure.step('Insert into admin'):
        with app.app_context():
            db = AndrewDB()
            db.insert_admin(10, "John", "Doe", "+0-000-00-00-00")


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_hotels(mock_connect):
    with allure.step('Get all hotels'):
        with app.app_context():
            db = AndrewDB()
            expected = ['hotel1']
            mock_connect().cursor.return_value.fetchone.return_value.__getitem__('hotels').return_value = expected
            result = db.get_all_hotels().return_value
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_sys_users(mock_connect):
    with allure.step('Get all system users'):
        with app.app_context():
            db = AndrewDB()
            expected = ['user1', 'user2']
            mock_connect().cursor.return_value.fetchone.return_value.__getitem__('users').return_value = expected
            result = db.get_all_system_users().return_value
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_db_statistics(mock_connect):
    with allure.step('Get db statistics'):
        with app.app_context():
            db = AndrewDB()
            expected = [{'cache_hit_ratio': 1.01, 'numbackends': 0}]
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_db_statistics()
        assert result == expected[0]


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_admins(mock_connect):
    with allure.step('Get all hotels'):
        with app.app_context():
            db = AndrewDB()
            expected = ['admin1', 'admin2']
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_all_admins()
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def get_room_by_params(mock_connect):
    with allure.step('Get room by parameters'):
        with app.app_context():
            db = AndrewDB()
            expected = ['room2', 'room1']
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_rooms_by_params("recep", "2018-01-02", "2018-01-10")
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_receptionists(mock_connect):
    with allure.step('Get all receptionists'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'user1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_all_receptionists(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_vw_hotel_by_id(mock_connect):
    with allure.step('Get vw hotel by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'hotel1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_vw_hotel_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_vw_customer_by_id(mock_connect):
    with allure.step('Get vw customer by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'customer1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_vw_customer_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_customer_by_id(mock_connect):
    with allure.step('Get customer by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'customer1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_customer_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_hotel_admin_by_id(mock_connect):
    with allure.step('Get hotel_admin by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'hotel_admin1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_hotel_admin_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_receptionist_by_id(mock_connect):
    with allure.step('Get receptionist by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'receptionist1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_receptionist_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_admin_by_id(mock_connect):
    with allure.step('Get admin by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'admin1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_admin_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_hotel_by_id(mock_connect):
    with allure.step('Get hotel by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: 'hotel1'}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_hotel_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_rooms_with_settings_by_id(mock_connect):
    with allure.step('Get rooms_with_settings by id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: "room1"}
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_rooms_with_settings_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_booked_rooms_by_hotel_id(mock_connect):
    with allure.step('Get booked rooms by hotel id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: "room1"}
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_rooms_with_settings_by_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_delete_transaction(mock_connect):
    with allure.step('Delete transaction'):
        with app.app_context():
            db = AndrewDB()
            db.delete_transaction(1)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_some_info_by_user_id(mock_connect):
    with allure.step('Get some info by user id'):
        with app.app_context():
            db = AndrewDB()
            expected = {1: "info"}
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_some_info_by_user_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_options_by_params(mock_connect):
    with allure.step('Get options by parameters'):
        with app.app_context():
            db = AndrewDB()
            expected = ["option1", "option2"]
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_option_by_params(True, True, True, True, True)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_option(mock_connect):
    with allure.step('Insert option'):
        with app.app_context():
            db = AndrewDB()
            expected = {'option_id': 1}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.insert_option(True, True, True, True, True)
        assert result == expected['option_id']


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_delete_room_by_id(mock_connect):
    with allure.step('Delete room by id'):
        with app.app_context():
            db = AndrewDB()
            db.delete_room_by_id(1)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_select_config_id(mock_connect):
    with allure.step('Select config id'):
        with app.app_context():
            db = AndrewDB()
            expected = 1
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.select_config(False, False, True)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_config(mock_connect):
    with allure.step('Insert config'):
        with app.app_context():
            db = AndrewDB()
            db.insert_config(True, False, False)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_setup_room_by_id(mock_connect):
    with allure.step('Set up room by id'):
        with app.app_context():
            db = AndrewDB()
            db.set_up_room_by_id(1, 1, 50, "room blue", "very blue room", 5000, 5)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_add_new_receptionist(mock_connect):
    with allure.step('Add receptionist'):
        with app.app_context():
            db = AndrewDB()
            db.add_new_receptionist(1, 1, "John", "Doe", "+0-000-00-00-00", 5000)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_add_new_room(mock_connect):
    with allure.step('Add new room'):
        with app.app_context():
            db = AndrewDB()
            db.add_new_room(1, 1, 1, 50, "room blue", "very blue room", 5000)


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_receptionists_by_hotel_id(mock_connect):
    with allure.step('Get receptionists of hotel'):
        with app.app_context():
            db = AndrewDB()
            expected = ["receptionist1", "receptionist2"]
            mock_connect().cursor.return_value.fetchall.return_value = expected
            result = db.get_receptionists_by_hotel_id(1)
        assert result == expected


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_get_cost_by_id(mock_connect):
    with allure.step('Get cost by room id'):
        with app.app_context():
            db = AndrewDB()
            expected = {'cost': 1}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.get_cost_by_id(1)
        assert result == expected['cost']


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def task_create_transaction_get_id(mock_connect):
    with allure.step('Create transaction and get id'):
        with app.app_context():
            db = AndrewDB()
            expected = {'transaction_id': 1}
            mock_connect().cursor.return_value.fetchone.return_value = expected
            result = db.create_transaction_get_id({})
        assert result == expected['transaction_id']


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_insert_location_if_not_exists(mock_connect):
    with allure.step('Add new room'):
        with app.app_context():
            db = AndrewDB()
            db.insert_location_if_not_exists("Russia", "Innopolis")


@allure.feature("Database")
@mock.patch("psycopg2.connect")
def test_add_hotel(mock_connect):
    with allure.step('Add hotel'):
        with app.app_context():
            db = AndrewDB()
            db.add_hotel("Moscow", "Innopolis", "NoName", 4, "Not named hotel", 1, "noname.png")



@allure.feature("Helpers")
def test_searchOp():
    """Test that seatchOp generates valid SQL queries"""

    def create_search_form(is_bathroom="no", is_tv="no", is_wifi="no", is_bathhub="no", is_airconditioniring="no"):
        return {
            'is_bathroom': is_bathroom,
            'is_tv': is_tv,
            'is_wifi': is_wifi,
            'is_bathhub': is_bathhub,
            'is_airconditioniring': is_airconditioniring
        }

    with allure.step("Check that empty form yields empty SQL query"):
        query = searchOp({})
        assert(len(query) == 0)

    with allure.step("[NEGATIVE] Check that non-empty form yields non-empty SQL query"):
        query = searchOp(create_search_form())
        assert (len(query) != 0)

    with allure.step("Check that invalid key do not affect query generation"):
        query = searchOp({'invalid': False})
        assert (len(query) == 0)

    with allure.step("Check validity of SQL query generation"):
        query = searchOp(create_search_form())
        assert (query ==
                "(ro.is_bathroom=%(is_bathroom)s AND "
                 "ro.is_tv=%(is_tv)s AND "
                 "ro.is_wifi=%(is_wifi)s AND "
                 "ro.is_bathhub=%(is_bathhub)s AND "
                 "ro.is_airconditioniring=%(is_airconditioniring)s)")
