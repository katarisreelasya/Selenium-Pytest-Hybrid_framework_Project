
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope='session')
def driver():
    ops = Options()
    ops.add_argument('--disable-notifications')
    ops.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=ops)
    yield driver
    driver.quit()
