import time
import unittest

from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException


class Register(LiveServerTestCase):
    login_and_pass = ''

    def create_app(self):
        app = Flask(__name__)
        return app

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test0_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test1_register(self):
        Register.login_and_pass = str(int(time.time()))

        driver = self.driver
        driver.get("http://127.0.0.1:5000/")
        driver.find_element_by_link_text("Register").click()
        driver.find_element_by_id("first_name").click()
        driver.find_element_by_id("first_name").clear()
        driver.find_element_by_id("first_name").send_keys(Register.login_and_pass)
        driver.find_element_by_id("last_name").click()
        driver.find_element_by_id("last_name").clear()
        driver.find_element_by_id("last_name").send_keys(Register.login_and_pass)
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(f"{Register.login_and_pass}@innopolis.ru")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(Register.login_and_pass)
        driver.find_element_by_id("password_confirmation").click()
        driver.find_element_by_id("password_confirmation").clear()
        driver.find_element_by_id("password_confirmation").send_keys(Register.login_and_pass)
        driver.find_element_by_id("telephone").click()
        driver.find_element_by_id("telephone").clear()
        driver.find_element_by_id("telephone").send_keys(Register.login_and_pass)
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def test2_search_and_book(self):
        driver = self.driver

        driver.get("http://127.0.0.1:5000/index")
        driver.find_element_by_link_text("Sign in").click()
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(Register.login_and_pass)
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(f"{Register.login_and_pass}@innopolis.ru")
        driver.find_element_by_id("password").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()

        driver.find_element_by_id("destination").click()
        driver.find_element_by_id("destination").clear()
        driver.find_element_by_id("destination").send_keys("e")
        driver.find_element_by_id("datepickerIn").send_keys("18-04-2018")
        driver.find_element_by_id("datepickerOut").send_keys("18-04-2018")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.find_element_by_id("info").click()
        driver.find_element_by_xpath("(//button[@type='button'])[2]").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to.alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
