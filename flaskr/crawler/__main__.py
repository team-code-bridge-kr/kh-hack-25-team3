from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

import time
import os
import json

from dotenv import load_dotenv

load_dotenv()

default_url = os.environ.get("DEFAULT_URL")


def main():

    def login():
        driver = webdriver.Firefox()

        driver.get(default_url)

        driver.get("https://kyungheeboy.riroschool.kr/user.php?action=signin")
        login_id = os.environ.get("USER_ID")
        login_pw = os.environ.get("USER_PW")
        driver.find_element(By.ID, "id").send_keys(login_id)
        driver.find_element(By.ID, "pw").send_keys(login_pw)

        login_button = driver.find_element(
            By.CSS_SELECTOR, "button.button_normal[type='button']"
        )
        login_button.click()

        return driver

    driver = login()

    from .riro_parts.riro_util import wait_select

    # 학사 일정
    wait_select(driver, By.CLASS_NAME, "btn_sch_pc").click()
    element = wait_select(driver, By.CLASS_NAME, "lds-wap")

    source = element.get_attribute("outerHTML")

    # import msg_board
    # msg_board.crawl(driver)

    # driver.find_element(By.CLASS_NAME, "btn_sch_pc").click()
    #
    # time.sleep(10)
    #
    # html = driver.find_element(By.CLASS_NAME, "lds-wap")
    # source = html.get_attribute("outerHTML")
    #
    # with open("bibi.html", "w") as file:
    #     file.write(source)
    #
    # driver.find_element(By.CLASS_NAME, "lds-wap")


if __name__ == "__main__":
    main()
