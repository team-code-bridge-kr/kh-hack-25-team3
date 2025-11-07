from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from crawler.riro_parts.riro_util import wait_select

import time
import os
import json

from dotenv import load_dotenv

load_dotenv()

default_url = os.environ.get("DEFAULT_URL")


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


def school_schedule(driver: WebDriver):
    wait_select(driver, By.CLASS_NAME, "btn_sch_pc").click()
    element = wait_select(driver, By.CLASS_NAME, "lds-wap")

    source = element.get_attribute("outerHTML")
    driver.get(default_url)
    return source


def meal_contents(driver: WebDriver):
    wait_select(driver, By.CLASS_NAME, "meal_icon").click()
    element = wait_select(driver, By.CLASS_NAME, "meal_day_contents_wrapper")

    source = element.get_attribute("outerHTML")
    driver.get(default_url)
    return source


def notice(driver: WebDriver, page):
    # wait_select(driver, By.CLASS_NAME, "re_menucon_li").click()
    driver.get(
        f"https://kyungheeboy.riroschool.kr/board_msg.php?club=index&action=list&Appwin=reload&db=1901&cate=&t_year=&sort=&uid=&page={page}&key=&key2=&s1=&s2=&s3="
    )

    wait_select(driver, By.CLASS_NAME, "rd_board")
    table = driver.find_element(By.CLASS_NAME, "rd_board")
    rows = table.find_elements(By.CSS_SELECTOR, "tr")  # 클래스 'set'인 tr만

    notice_html_list = []
    submit_html_list = []
    end_html_list = []

    # ───────────────────────────────
    # 3️⃣ 각 행에서 필요한 데이터 추출
    # ───────────────────────────────
    for row in rows:
        try:
            # link = row.find_element(By.TAG_NAME, "a").click()
            # url = driver.current_url
            # print(url)
            #
            # driver.back()

            status = row.find_element(By.CSS_SELECTOR, ".rd_status").text.strip()
            title_elem = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4) a")
            title = title_elem.text.strip()
            # link = title_elem.get_attribute(
            #     "href"
            # )  # href가 javascript:bL(...)이면 그대로 가져오거나 파싱 가능
            teacher = row.find_element(
                By.CSS_SELECTOR, "td:nth-of-type(6)"
            ).text.strip()
            date = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(8)").text.strip()
        except Exception:
            continue  # 형식이 안 맞으면 건너뛰기

        post = {
            "title": title,
            "link": "",
            "teacher": teacher,
            "date": date,
            # "link": "https://www.youtube.com/watch?v=bL_BL44u794",
        }

        if status == "알림":
            notice_html_list.append(post)
        elif status == "제출":
            submit_html_list.append(post)
        elif status == "마감":
            end_html_list.append(post)
        # '마감' 등은 필요 없으면 무시

    driver.get(default_url)
    return notice_html_list, submit_html_list, end_html_list
