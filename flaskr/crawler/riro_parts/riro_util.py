from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_select(driver: WebDriver, by: By.ID, name: str):
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((by, name))
    )
    return element
