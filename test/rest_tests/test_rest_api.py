import unittest

import allure
import requests


class RESTAPITest(unittest.TestCase):
    url = 'http://localhost:5000'
    OK = 200
    NOT_FOUND = 404
    ERROR = 500
    session = requests.Session()

    @allure.step('Index page accessibility')
    def test_index_page_accessibility(self):
        self.assertEqual(self.session.get(f'{self.url}').status_code, self.OK)
        self.assertEqual(self.session.get(f'{self.url}/').status_code, self.OK)
        self.assertEqual(self.session.get(f'{self.url}/index').status_code, self.OK)
        self.assertEqual(self.session.get(f'{self.url}/abracadabra').status_code, self.NOT_FOUND)

    @allure.step('Hotel searching')
    def test_hotel_searching(self):
        check_in_d = '25-04-2018'
        check_out_d = '26-04-2018'
        destination = 'e'
        search_url = f'{self.url}/search-hotel?checkin={check_in_d}&checkout={check_out_d}&destination={destination}'
        req = self.session.get(search_url)
        self.assertEqual(req.status_code, self.ERROR)

    @allure.step('Hotel info by id')
    def test_hotel_info(self):
        search_url = f'{self.url}/more-info/1'
        req = self.session.get(search_url)
        self.assertEqual(req.status_code, self.ERROR)
