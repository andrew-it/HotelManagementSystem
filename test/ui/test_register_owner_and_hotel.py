import time
import unittest

import allure
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select


class AddNewHotelOwner(unittest.TestCase):
    login_and_pass = ''

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    @allure.step('Hotel\'s owner registration')
    def test1_add_new_hotel_owner(self):
        AddNewHotelOwner.login_and_pass = str(int(time.time()))

        driver = self.driver
        driver.get("http://127.0.0.1:5000/index")
        driver.find_element_by_link_text("Add your property").click()
        driver.find_element_by_id("first_name").click()
        driver.find_element_by_id("first_name").clear()
        driver.find_element_by_id("first_name").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("last_name").click()
        driver.find_element_by_id("last_name").clear()
        driver.find_element_by_id("last_name").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(f"{AddNewHotelOwner.login_and_pass}@innopolis.ru")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("password_confirmation").click()
        driver.find_element_by_id("password_confirmation").clear()
        driver.find_element_by_id("password_confirmation").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("telephone").click()
        driver.find_element_by_id("telephone").clear()
        driver.find_element_by_id("telephone").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_xpath("//button[@type='submit']").click()

    @allure.step('New hotel adding')
    def test2_add_new_hotel(self):
        driver = self.driver

        driver.get("http://127.0.0.1:5000/index")
        driver.find_element_by_link_text("Sign in").click()
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(f"{AddNewHotelOwner.login_and_pass}@innopolis.ru")
        driver.find_element_by_id("password").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()

        # driver.get("http://127.0.0.1:5000/")
        # driver.find_element_by_partial_link_text("My hotels").click()
        driver.find_element_by_id("add_hotel").click()
        driver.find_element_by_id("hotel_name").click()
        driver.find_element_by_id("hotel_name").clear()
        driver.find_element_by_id("hotel_name").send_keys(AddNewHotelOwner.login_and_pass)
        driver.find_element_by_id("country").click()
        driver.find_element_by_id("country").clear()
        driver.find_element_by_id("country").send_keys("Russia")
        driver.find_element_by_id("city").click()
        driver.find_element_by_id("city").clear()
        driver.find_element_by_id("city").send_keys("Innopolis")
        driver.find_element_by_id("address").click()
        driver.find_element_by_id("address").clear()
        driver.find_element_by_id("address").send_keys("Universitetskaya")
        driver.find_element_by_id("description").click()
        Select(driver.find_element_by_id("stars")).select_by_visible_text("5")
        driver.find_element_by_xpath("//option[@value='5']").click()
        # driver.find_element_by_xpath("//div[2]/div/label").click()
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
