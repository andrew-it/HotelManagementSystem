import nose
import requests


def test_REST_API():
    url = 'http://localhost:5000'
    OK = 200
    NOT_FOUND = 404
    ERROR = 500
    session = requests.Session()

    with nose.allure.step('Index page accessibility'):
        assert (session.get(f'{url}').status_code == OK)
        assert (session.get(f'{url}/').status_code == OK)
        assert (session.get(f'{url}/index').status_code == OK)
        assert (session.get(f'{url}/abracadabra').status_code == NOT_FOUND)

    with nose.allure.step('Hotel searching'):
        check_in_d = '2018-04-25'
        check_out_d = '2018-04-26'
        destination = 'e'
        search_url = f'{url}/search-hotel?checkin={check_in_d}&checkout={check_out_d}&destination={destination}'
        req = session.get(search_url)
        assert (req.status_code == OK)

    with nose.allure.step('Hotel info by id'):
        search_url = f'{url}/more-info/1'
        req = session.get(search_url)
        assert (req.status_code == OK)

    with nose.allure.step('Hotel info by id'):
        pass
