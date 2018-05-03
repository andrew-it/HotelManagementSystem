import time
import allure
from selenium.webdriver.support.ui import Select

from time import sleep


@allure.feature('UI')
def test_add_ne_hotel_owner(browser):
    """Test Hotel Owner registration and Hotel creation"""
    driver = browser
    with allure.step('Hotel\'s owner registration'):
        login_and_pass = str(int(time.time()))

        driver.get("http://127.0.0.1:5000/index")
        driver.find_element_by_link_text("Add your property").click()
        driver.find_element_by_id("first_name").click()
        driver.find_element_by_id("first_name").clear()
        driver.find_element_by_id("first_name").send_keys(login_and_pass)
        driver.find_element_by_id("last_name").click()
        driver.find_element_by_id("last_name").clear()
        driver.find_element_by_id("last_name").send_keys(login_and_pass)
        driver.find_element_by_id("email").click()
        driver.find_element_by_id("email").clear()
        driver.find_element_by_id("email").send_keys(f"{login_and_pass}@innopolis.ru")
        driver.find_element_by_id("password").click()
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(login_and_pass)
        driver.find_element_by_id("password_confirmation").click()
        driver.find_element_by_id("password_confirmation").clear()
        driver.find_element_by_id("password_confirmation").send_keys(login_and_pass)
        driver.find_element_by_id("telephone").click()
        driver.find_element_by_id("telephone").clear()
        driver.find_element_by_id("telephone").send_keys(login_and_pass)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        assert (True)

    with allure.step('New hotel adding'):
        driver.get("http://127.0.0.1:5000/index")
        # driver.implicitly_wait(10)
        # driver.find_element_by_link_text("Sign in").click()
        # driver.implicitly_wait(10)
        # driver.find_element_by_id("email").click()
        # driver.find_element_by_id("password").clear()
        # driver.find_element_by_id("password").send_keys(login_and_pass)
        # driver.find_element_by_id("email").click()
        # driver.find_element_by_id("email").clear()
        # driver.find_element_by_id("email").send_keys(f"{login_and_pass}@innopolis.ru")
        # driver.find_element_by_id("password").click()
        # driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.implicitly_wait(10)

        # driver.get("http://127.0.0.1:5000/")
        driver.find_element_by_partial_link_text("My hotels").click()
        driver.implicitly_wait(10)
        driver.find_element_by_id("add_hotel").click()
        driver.implicitly_wait(10)
        driver.find_element_by_id("hotel_name").click()
        driver.find_element_by_id("hotel_name").clear()
        driver.find_element_by_id("hotel_name").send_keys(login_and_pass)
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
        driver.implicitly_wait(10)
        assert (True)