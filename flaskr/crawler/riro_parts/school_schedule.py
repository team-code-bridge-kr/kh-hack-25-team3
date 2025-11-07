from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from riro_parts.riro_util import wait_select


def crawl(driver: WebDriver):
    wait_select(driver, By.CLASS_NAME, "btn_sch_pc").click()
    element = wait_select(driver, By.CLASS_NAME, "lds-wap")

    source = element.get_attribute("outerHTML")
    return source
