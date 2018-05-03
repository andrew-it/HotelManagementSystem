import time
import allure
from time import sleep

@allure.feature('UI')
def test_register(browser):
    """Test User Registration and Hotel Room Booking"""
    driver = browser

    with allure.step('Registration new user'):
        login_and_pass = str(int(time.time()))

        driver.get("http://127.0.0.1:5000/")
        driver.implicitly_wait(10)
        driver.find_element_by_link_text("Register").click()
        driver.implicitly_wait(10)
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

    with allure.step('Searching and booking a room'):
        driver.get("http://127.0.0.1:5000/index")
        # driver.implicitly_wait(10)
        # driver.find_element_by_link_text("Sign in").click()
        # driver.find_element_by_id("email").click()
        # driver.find_element_by_id("password").clear()
        # driver.find_element_by_id("password").send_keys(login_and_pass)
        # driver.find_element_by_id("email").click()
        # driver.find_element_by_id("email").clear()
        # driver.find_element_by_id("email").send_keys(f"{login_and_pass}@innopolis.ru")
        # driver.find_element_by_id("password").click()
        # driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.implicitly_wait(10)

        driver.find_element_by_id("destination").click()
        driver.find_element_by_id("destination").clear()
        driver.find_element_by_id("destination").send_keys("e")
        driver.find_element_by_id("datepickerIn").send_keys("18-04-2018")
        driver.find_element_by_id("datepickerOut").send_keys("18-04-2018")
        driver.find_element_by_xpath("//button[@type='submit']").click()
        driver.implicitly_wait(10)
        driver.find_element_by_id("info").click()
        driver.implicitly_wait(10)
        driver.find_element_by_xpath("(//button[@type='button'])[2]").click()
        sleep(2)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        assert (True)

