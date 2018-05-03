import pytest
from selenium import webdriver


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument('--no-sandbox')

@pytest.yield_fixture()
def browser(request):
    driver = webdriver.Chrome(chrome_options=chrome_options)
    yield driver
    driver.quit()
