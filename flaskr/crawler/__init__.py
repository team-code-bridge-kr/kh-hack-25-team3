from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os
import json

from dotenv import load_dotenv

load_dotenv()


driver = webdriver.Firefox()

driver.get("https://kyungheeboy.riroschool.kr")


def login():
    driver.get("https://kyungheeboy.riroschool.kr/user.php?action=signin")
    login_id = os.environ.get("USER_ID")
    login_pw = os.environ.get("USER_PW")
    driver.find_element(By.ID, "id").send_keys(login_id)
    driver.find_element(By.ID, "pw").send_keys(login_pw)

    login_button = driver.find_element(
        By.CSS_SELECTOR, "button.button_normal[type='button']"
    )
    login_button.click()


# def get_cookies():
#     with open("/home/jiho/riroBackShoter/crawler/cookie.txt", "w") as sessionFile:
#         newList = []
#         for cookie in driver.get_cookies():
#             newCookie = {"name": cookie["name"], "value": cookie["value"]}
#             newList.append(newCookie)
#
#         sessionFile.write(json.dumps(newList))
#
#
# def load_cookies():
#     with open("/home/jiho/riroBackShoter/crawler/cookie.txt", "r") as sessionFile:
#         newList = sessionFile.read()
#         cookies = json.loads(newList)
#
#         for cookie in cookies:
#             driver.delete_cookie(cookie["name"])
#             driver.add_cookie(cookie)
#

login()
