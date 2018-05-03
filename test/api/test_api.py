import time

import allure
import requests

from app import app

url = 'http://localhost:5000'
OK = 200
FOUND = 302
NOT_FOUND = 404
NOT_ALLOWED = 405
ERROR = 500
req_session = requests.Session()
client = app.test_client()
owner = app.test_client()

curr_time = str(int(time.time()))
registration_data = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time + '@inno.ru',
                     'password': curr_time, 'password_confirmation': curr_time, 'telephone': curr_time}
registration_data_broken_pass = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time + '11@inno.ru',
                                 'password': curr_time, 'password_confirmation': '111', 'telephone': curr_time}
registration_data_broken_email = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time,
                                  'password': curr_time, 'password_confirmation': curr_time, 'telephone': curr_time}


@allure.feature('API')
def test_registration():
    """Registration tests with several cases"""
    with allure.step('Registration new user'):
        register_url = f'{url}/register'
        req = client.post(register_url, data=registration_data)
        assert req.status_code == FOUND
        assert 'index' in req.location

    with allure.step('Registration with different password and confirm password'):
        req = client.post(register_url, data=registration_data_broken_pass)
        assert req.status_code == OK

    with allure.step('Registration new user with the same email'):
        req = client.post(register_url, data=registration_data)
        assert req.status_code == FOUND
        assert 'register' in req.location

    with allure.step('[NEGATIVE]: empty fields'):
        req = client.post(register_url, data={})
        assert req.status_code == OK
        assert req.location is None

    with allure.step('[NEGATIVE]: missed fields'):
        req = client.post(register_url, data={'first_name': curr_time})
        assert req.status_code == OK
        assert req.location is None

    with allure.step('[NEGATIVE]: broken email'):
        req = client.post(register_url, data=registration_data_broken_email)
        assert req.status_code == FOUND
        assert 'index' in req.location

    with allure.step('Logout'):
        logout_url = f'{url}/logout'
        req = client.post(logout_url, data=registration_data)
        assert req.status_code == NOT_ALLOWED

    with allure.step('Login'):
        login_url = f'{url}/login'
        req = client.post(login_url, data=registration_data)
        assert req.status_code == FOUND
        assert 'index' in req.location


@allure.feature('API')
def test_index_accessibility():
    """Simple test of index page accessibility"""
    with allure.step('Index page accessibility'):
        assert req_session.get(f'{url}').status_code == OK
        assert req_session.get(f'{url}/').status_code == OK
        assert req_session.get(f'{url}/index').status_code == OK
    with allure.step('[NEGATIVE]: unexisting link'):
        assert req_session.get(f'{url}/abracadabra').status_code == NOT_FOUND


@allure.feature('API')
def test_hotel_searching():
    """Search hotel by 'destination', 'checkin', 'checkout' and other parameters"""
    request_data = {'destination': 'e', 'checkin': '02-05-2018', 'checkout': '03-05-2018', 'is_bathroom': False,
                    'is_tv': False, 'is_wifi': False, 'is_bathhub': False, 'is_airconditioniring': False,
                    'sleeps': 1, 'price_from': 0, 'price_to': 0, 'quantity': 1}
    with allure.step('Hotel searching'):
        search_url = f'{url}/'
        req = client.post(search_url, data=request_data)
        assert req.status_code == FOUND
        assert 'search-hotel' in req.location

    with allure.step('Search hotel'):
        search_url = f'{url}/search-hotel'
        hotel_id_data = {'hotel_id': '1'}
        req = client.post(search_url, data=hotel_id_data)
        assert req.status_code == FOUND
        assert 'more-info' in req.location

    with allure.step('Search hotel'):
        req = client.get(search_url)
        assert req.status_code == OK

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(search_url, data={})
        assert req.status_code == ERROR


@allure.feature('API')
def test_more_info():
    """Get more info about hotel"""
    request_data = {'destination': 'e', 'checkin': '02-05-2018', 'checkout': '03-05-2018', 'is_bathroom': False,
                    'is_tv': False, 'is_wifi': False, 'is_bathhub': False, 'is_airconditioniring': False,
                    'sleeps': 1, 'price_from': 0, 'price_to': 0, 'quantity': 1, 'hotel_id': '2'}

    with allure.step('Search hotel by id: with request data'):
        search_url = f'{url}/search-hotel/2'
        req = client.post(search_url, data=request_data)
        assert req.status_code >= FOUND

    with allure.step('Search hotel by id: with hotel id'):
        search_url = f'{url}/search-hotel/2'
        hotel_id_data = {'hotel_id': '1'}
        req = client.post(search_url, data=hotel_id_data)
        assert req.status_code >= FOUND

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(search_url, data={})
        assert req.status_code == NOT_FOUND


curr_time = str(int(time.time()))
owner_data = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time + '@inno.ru',
              'password': curr_time, 'password_confirmation': curr_time, 'telephone': curr_time}
owner_data_broken_pass = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time + '@inno.ru',
                          'password': curr_time, 'password_confirmation': '11', 'telephone': curr_time}
owner_data_existing_email = {'first_name': curr_time, 'last_name': curr_time, 'email': curr_time + '@inno.ru',
                             'password': curr_time, 'password_confirmation': curr_time, 'telephone': curr_time}


@allure.feature('API')
def test_add_property():
    """Add new hotel"""
    url_link = f'{url}/add-property'
    with allure.step('Add property with broken password'):
        req = owner.post(url_link, data=owner_data_broken_pass)
        assert req.status_code == OK

    with allure.step('Add property with same email'):
        req = owner.post(url_link, data=owner_data_existing_email)
        assert req.status_code == FOUND
        # assert 'add-property' in req.location

    with allure.step('Add property success'):
        req = owner.post(url_link, data=owner_data)
        assert req.status_code == FOUND
        assert 'add-property' in req.location

    with allure.step('[NEGATIVE]: Customer as owner'):
        req = owner.post(url_link, data=registration_data)
        assert req.status_code == FOUND
        assert 'add-property' in req.location

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(url_link, data={})
        assert req.status_code == OK


@allure.feature('API')
def test_get_profile():
    """Get profile of some user"""
    with allure.step('Get person`s profile'):
        profile_url = f'{url}/profile'
        req = owner.get(profile_url, data=owner_data)
        assert req.status_code == OK

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(profile_url, data={})
        assert req.status_code == FOUND
        assert 'index' in req.location


@allure.feature('API')
def test_update_profile():
    """Update profile of some user"""
    with allure.step('Update person`s profile'):
        profile_url = f'{url}/profile'
        req = owner.post(profile_url, data=owner_data)
        assert req.status_code == FOUND
        assert 'index' in req.location

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(profile_url, data={})
        assert req.status_code == FOUND
        assert 'index' in req.location


@allure.feature('API')
def test_my_hotels():
    """Get all owner's hotels"""
    with allure.step('Get owners`s hotels: POST'):
        hotel_url = f'{url}/my-hotel'
        req = owner.post(hotel_url, data=owner_data)
        assert req.status_code == FOUND
        assert 'login' in req.location

    with allure.step('Get owners`s hotels: GET'):
        hotel_url = f'{url}/my-hotel'
        req = owner.get(hotel_url, data=owner_data)
        assert req.status_code == FOUND
        assert 'login' in req.location

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(hotel_url, data={})
        assert req.status_code == FOUND
        assert 'login' in req.location


@allure.feature('API')
def test_add_hotel():
    """Add new hotel"""
    with allure.step('Add hotel'):
        add_hotel_url = f'{url}/add-hotel'
        req = owner.post(add_hotel_url, data=owner_data)
        assert req.status_code == FOUND
        assert 'login' in req.location

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(add_hotel_url, data={})
        assert req.status_code == FOUND
        assert 'login' in req.location


@allure.feature('API')
def test_edit_hotel():
    """Hotel information editing"""
    with allure.step('Edit hotel'):
        edit_hotel_url = f'{url}/edit-hotel'
        req = owner.post(edit_hotel_url, data=owner_data)
        assert req.status_code == NOT_FOUND

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(edit_hotel_url, data={})
        assert req.status_code == NOT_FOUND


@allure.feature('API')
def test_manage_hotel():
    """Manage hotel testing"""
    with allure.step('Manage hotel'):
        manage_hotel_url = f'{url}/manage-hotel/1'
        req = owner.post(manage_hotel_url, data=owner_data)
        assert req.status_code == FOUND
        assert 'login' in req.location

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(manage_hotel_url, data={})
        assert req.status_code == FOUND
        assert 'login' in req.location


@allure.feature('API')
def test_my_booking():
    """Customer's booking list testing"""
    with allure.step('My booking'):
        my_booking_url = f'{url}/my-booking'
        req = owner.post(my_booking_url, data=owner_data)
        assert req.status_code == OK

    with allure.step('[NEGATIVE]: Empty data'):
        req = owner.post(my_booking_url, data={})
        assert req.status_code == OK


@allure.feature('API')
def test_manage_booking():
    """Booking manage testing"""
    with allure.step('Manage booking'):
        manage_booking_url = f'{url}/manage-booking'
        req = owner.post(manage_booking_url, data=owner_data)
        assert req.status_code == ERROR

    with allure.step('[NEGATIVE] [EXPECT ERROR]: Empty data'):
        req = owner.post(manage_booking_url, data={})
        assert req.status_code == ERROR


@allure.feature('API')
def test_new_booking():
    """Creating new booking testing"""
    with allure.step('New booking'):
        new_booking_url = f'{url}/new-booking'
        req = owner.post(new_booking_url, data=registration_data)
        assert req.status_code == ERROR

    with allure.step('[NEGATIVE] [EXPECT ERROR]: Empty data'):
        req = owner.post(new_booking_url, data={})
        assert req.status_code == ERROR


@allure.feature('API')
def test_admin():
    """Admin panel testing"""
    with allure.step('Admin panel'):
        admin_panel_url = f'{url}/admin-panel'
        req = owner.post(admin_panel_url, data=owner_data)
        assert req.status_code == ERROR

    with allure.step('[NEGATIVE] [EXPECT ERROR]: Empty data'):
        req = owner.post(admin_panel_url, data={})
        assert req.status_code == ERROR
