from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from .riro_parts.riro_util import wait_select

import time
import os
import json
import re

from dotenv import load_dotenv

# .env 파일을 여러 경로에서 찾기
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),  # flaskr/crawler/.env
    os.path.join(os.path.dirname(__file__), '..', '..', '.env'),  # 프로젝트 루트/.env
    os.path.join(os.path.dirname(__file__), '..', '.env'),  # flaskr/.env
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break
else:
    # .env 파일을 찾지 못하면 기본 경로에서 로드 시도
    load_dotenv()

default_url = os.environ.get("DEFAULT_URL") or "https://kyungheeboy.riroschool.kr"


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
    """공지사항 크롤링 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        page: 페이지 번호
        
    Returns:
        tuple: (notice_list, submit_list, end_list)
    """
    driver.get(
        f"https://kyungheeboy.riroschool.kr/board_msg.php?club=index&action=list&Appwin=reload&db=1901&cate=&t_year=&sort=&uid=&page={page}&key=&key2=&s1=&s2=&s3="
    )

    wait_select(driver, By.CLASS_NAME, "rd_board")
    table = driver.find_element(By.CLASS_NAME, "rd_board")
    rows = table.find_elements(By.CSS_SELECTOR, "tr")

    notice_html_list = []
    submit_html_list = []
    end_html_list = []

    # 각 행에서 필요한 데이터 추출
    for idx, row in enumerate(rows, 1):
        # 변수 초기화 (스코프 문제 해결)
        status = None
        title = None
        teacher = None
        date = None
        url = ""

        try:
            # 상태 추출
            status = row.find_element(By.CSS_SELECTOR, ".rd_status").text.strip()
            
            # 제목 추출
            title_elem = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(4) a")
            title = title_elem.text.strip()
            
            # 선생님 추출
            teacher = row.find_element(
                By.CSS_SELECTOR, "td:nth-of-type(6)"
            ).text.strip()
            
            # 날짜 추출
            date = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(8)").text.strip()
            
            # 링크 URL 추출 (페이지 이동 없이 직접 추출)
            try:
                link_elem = row.find_element(By.CSS_SELECTOR, "td[style*='text-align:left'] a")
                
                # href 속성 확인
                href_value = link_elem.get_attribute("href") or ""
                onclick_value = link_elem.get_attribute("onclick") or ""
                
                url = ""
                uid = None
                
                # href에서 javascript:bL(...) 형태 파싱
                # 예: javascript:bL(1,5038,0); 또는 javascript:bL('view', '5038', ...)
                if href_value.startswith("javascript:"):
                    # bL(1,5038,0) 형태: 두 번째 파라미터가 uid
                    match = re.search(r"bL\([^,]+,\s*(\d+)", href_value)
                    if match:
                        uid = match.group(1)
                    # bL('view', '5038', ...) 형태
                    else:
                        match = re.search(r"bL\(['\"]view['\"],\s*['\"](\d+)['\"]", href_value)
                        if match:
                            uid = match.group(1)
                
                # onclick에서 추출 시도
                if not uid and onclick_value:
                    # bL('view', '5038', ...) 형태
                    match = re.search(r"bL\(['\"]view['\"],\s*['\"](\d+)['\"]", onclick_value)
                    if match:
                        uid = match.group(1)
                    # bL(1,5038,0) 형태
                    else:
                        match = re.search(r"bL\([^,]+,\s*(\d+)", onclick_value)
                        if match:
                            uid = match.group(1)
                
                # uid를 찾았으면 실제 URL 생성
                if uid:
                    url = f"https://kyungheeboy.riroschool.kr/board_msg.php?club=index&action=view&db=1901&page={page}&cate=&t_year=&sort=&uid={uid}&inum=0&key=&key2=&s1=&s2=&s3="
                    print(f"✅ 행 {idx} URL 추출 성공 (uid={uid}): {url[:80]}...")
                elif href_value and not href_value.startswith("javascript:"):
                    # 일반 URL인 경우 그대로 사용
                    url = href_value
                    print(f"✅ 행 {idx} URL 추출 성공 (직접 URL): {url[:80]}...")
                else:
                    print(f"⚠️ 행 {idx} URL 추출 실패: uid를 찾을 수 없음 (href: {href_value[:50]}, onclick: {onclick_value[:50]})")
            except Exception as e:
                # 링크 추출 실패 시 빈 문자열 유지
                url = ""
                print(f"❌ 링크 추출 실패 (행 {idx}): {type(e).__name__} - {str(e)[:50]}")

            # 데이터 검증
            if not all([status, title, teacher, date]):
                print(f"행 {idx}: 필수 데이터 누락 - 건너뛰기")
                continue

            # Post 딕셔너리 생성
            post = {
                "title": title,
                "link": url,  # URL 할당
                "teacher": teacher,
                "date": date,
            }
            
            # URL 저장 확인 로그
            print(f"📝 행 {idx} 저장: title='{title[:30]}...', link='{url[:60] if url else '없음'}...', status='{status}'")

            # 상태에 따라 분류
            if status == "알림":
                notice_html_list.append(post)
                print(f"  → 알림 리스트에 추가됨 (총 {len(notice_html_list)}개)")
            elif status == "제출":
                submit_html_list.append(post)
                print(f"  → 제출 리스트에 추가됨 (총 {len(submit_html_list)}개)")
            elif status == "마감":
                end_html_list.append(post)
                print(f"  → 마감 리스트에 추가됨 (총 {len(end_html_list)}개)")

        except Exception as e:
            # 구체적인 예외 정보 출력 (디버깅용)
            print(f"행 {idx} 처리 중 오류: {type(e).__name__} - {str(e)}")
            continue

    # 최종 결과 요약
    print(f"\n📊 크롤링 완료:")
    print(f"  - 알림: {len(notice_html_list)}개")
    print(f"  - 제출: {len(submit_html_list)}개")
    print(f"  - 마감: {len(end_html_list)}개")
    print(f"  - 총계: {len(notice_html_list) + len(submit_html_list) + len(end_html_list)}개")
    
    driver.get(default_url)
    return notice_html_list, submit_html_list, end_html_list


def task(driver: WebDriver, page):
    """수행평가 크롤링 함수
    
    Args:
        driver: Selenium WebDriver 인스턴스
        page: 페이지 번호
        
    Returns:
        tuple: (notice_list, submit_list, end_list)
    """
    driver.get(
        f"https://kyungheeboy.riroschool.kr/portfolio.php?db=1551&t_doc=0&cate=0&page={page}&key=&key2=&s1=&s2=&s3="
    )

    # HTML 구조 확인을 위한 디버깅
    try:
        wait_select(driver, By.CLASS_NAME, "rd_board")
        table = driver.find_element(By.CLASS_NAME, "rd_board")
        rows = table.find_elements(By.CSS_SELECTOR, "tr")
        print(f"✅ 테이블 발견: {len(rows)}개 행")
        
        # 첫 번째 행의 HTML 구조 확인
        if len(rows) > 0:
            first_row_html = rows[0].get_attribute("outerHTML")
            print(f"🔍 첫 번째 행 HTML (처음 500자): {first_row_html[:500]}")
    except Exception as e:
        print(f"❌ 테이블 찾기 실패: {e}")
        # 대체 셀렉터 시도
        try:
            # 다른 가능한 테이블 클래스명 시도
            table = driver.find_element(By.CSS_SELECTOR, "table")
            rows = table.find_elements(By.CSS_SELECTOR, "tr")
            print(f"✅ 대체 테이블 발견: {len(rows)}개 행")
        except:
            # 페이지 HTML 일부 출력
            page_source = driver.page_source[:2000]
            print(f"🔍 페이지 HTML (처음 2000자): {page_source}")
            raise Exception("테이블을 찾을 수 없습니다")
    
    rows = table.find_elements(By.CSS_SELECTOR, "tr")

    notice_html_list = []
    submit_html_list = []
    end_html_list = []

    # 각 행에서 필요한 데이터 추출
    for idx, row in enumerate(rows, 1):
        # 변수 초기화 (스코프 문제 해결)
        status = None
        title = None
        teacher = None
        date = None
        url = ""

        try:
            # 헤더 행 확인 (th 요소가 있으면 건너뛰기)
            ths = row.find_elements(By.CSS_SELECTOR, "th")
            if ths:
                print(f"🔍 [TASK] 행 {idx}는 헤더 행 - 건너뛰기")
                continue
            
            # 모든 td 요소 가져오기
            tds = row.find_elements(By.CSS_SELECTOR, "td")
            
            # 두 번째 행(첫 번째 데이터 행)의 구조 확인 (디버깅)
            if idx == 2 and len(tds) > 0:
                print(f"🔍 [TASK] 행 {idx} (첫 데이터 행) td 개수: {len(tds)}")
                for i, td in enumerate(tds, 1):
                    td_text = td.text.strip()[:80]
                    td_html = td.get_attribute("outerHTML")[:200]
                    print(f"  [TASK] td[{i}]: '{td_text}'")
                    print(f"    HTML: {td_html}")
                row_html = row.get_attribute("outerHTML")[:1000]
                print(f"🔍 [TASK] 행 {idx} 전체 HTML: {row_html}")
            
            # 상태 추출 - 여러 방법 시도
            status = ""
            try:
                status = row.find_element(By.CSS_SELECTOR, ".rd_status").text.strip()
            except:
                # 대체: 첫 번째 td에서 상태 찾기
                if len(tds) > 0:
                    status = tds[0].text.strip()
            
            # 제목 추출 - 여러 방법 시도
            title = ""
            try:
                # 먼저 모든 링크 찾기
                links = row.find_elements(By.CSS_SELECTOR, "td a")
                if links:
                    # 링크가 있으면 링크 텍스트를 제목으로 사용
                    for link in links:
                        link_text = link.text.strip()
                        if link_text and len(link_text) > 3:  # 의미있는 텍스트인지 확인
                            title = link_text
                            break
                    
                    # 링크 텍스트가 없으면 링크가 있는 td의 전체 텍스트 사용
                    if not title and links:
                        try:
                            parent_td = links[0].find_element(By.XPATH, "./..")
                            title = parent_td.text.strip()
                        except:
                            pass
                
                # 링크에서 찾지 못했으면 td 텍스트에서 찾기
                if not title:
                    # 일반적으로 제목은 2번째나 3번째 td에 있음 (portfolio.php 구조)
                    if len(tds) > 2:
                        # 2번째 td 시도
                        title = tds[1].text.strip()
                        if not title or len(title) < 3:
                            # 3번째 td 시도
                            if len(tds) > 2:
                                title = tds[2].text.strip()
                    elif len(tds) > 1:
                        title = tds[1].text.strip()
                
                # 여전히 없으면 모든 td에서 가장 긴 텍스트 찾기
                if not title:
                    max_len = 0
                    for td in tds:
                        td_text = td.text.strip()
                        if len(td_text) > max_len and len(td_text) > 5:
                            title = td_text
                            max_len = len(td_text)
                            
            except Exception as e:
                print(f"⚠️ [TASK] 행 {idx} 제목 추출 실패: {e}")
                # 마지막 시도: 모든 td 텍스트 조합
                if len(tds) > 2:
                    title = tds[2].text.strip()
            
            # 선생님 추출 - 여러 방법 시도
            teacher = ""
            try:
                teacher = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(6)").text.strip()
            except:
                if len(tds) > 5:
                    teacher = tds[5].text.strip()
                elif len(tds) > 4:
                    teacher = tds[4].text.strip()
            
            # 날짜 추출 - 여러 방법 시도
            date = ""
            try:
                date = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(8)").text.strip()
            except:
                if len(tds) > 7:
                    date = tds[7].text.strip()
                elif len(tds) > 6:
                    date = tds[6].text.strip()
                elif len(tds) > 5:
                    date = tds[5].text.strip()
            
            # 링크 URL 추출 (페이지 이동 없이 직접 추출)
            try:
                # 여러 방법으로 링크 찾기
                link_elem = None
                try:
                    link_elem = row.find_element(By.CSS_SELECTOR, "td[style*='text-align:left'] a")
                except:
                    try:
                        # 모든 td에서 링크 찾기
                        links = row.find_elements(By.CSS_SELECTOR, "td a")
                        if links:
                            link_elem = links[0]
                    except:
                        pass
                
                if link_elem:
                    # href 속성 확인
                    href_value = link_elem.get_attribute("href") or ""
                    onclick_value = link_elem.get_attribute("onclick") or ""
                    
                    url = ""
                    uid = None
                    
                    # href에서 javascript:bL(...) 형태 파싱
                    # 예: javascript:bL(1,5038,0); 또는 javascript:bL('view', '5038', ...)
                    if href_value.startswith("javascript:"):
                        # bL(1,5038,0) 형태: 두 번째 파라미터가 uid
                        match = re.search(r"bL\([^,]+,\s*(\d+)", href_value)
                        if match:
                            uid = match.group(1)
                        # bL('view', '5038', ...) 형태
                        else:
                            match = re.search(r"bL\(['\"]view['\"],\s*['\"](\d+)['\"]", href_value)
                            if match:
                                uid = match.group(1)
                    
                    # onclick에서 추출 시도
                    if not uid and onclick_value:
                        # bL('view', '5038', ...) 형태
                        match = re.search(r"bL\(['\"]view['\"],\s*['\"](\d+)['\"]", onclick_value)
                        if match:
                            uid = match.group(1)
                        # bL(1,5038,0) 형태
                        else:
                            match = re.search(r"bL\([^,]+,\s*(\d+)", onclick_value)
                            if match:
                                uid = match.group(1)
                    
                    # uid를 찾았으면 실제 URL 생성 (portfolio.php 사용)
                    if uid:
                        url = f"https://kyungheeboy.riroschool.kr/portfolio.php?db=1551&action=view&uid={uid}&page={page}&cate=0&t_doc=0&key=&key2=&s1=&s2=&s3="
                        print(f"✅ [TASK] 행 {idx} URL 추출 성공 (uid={uid}): {url[:80]}...")
                    elif href_value and not href_value.startswith("javascript:"):
                        # 일반 URL인 경우 그대로 사용
                        url = href_value
                        print(f"✅ [TASK] 행 {idx} URL 추출 성공 (직접 URL): {url[:80]}...")
                    else:
                        print(f"⚠️ [TASK] 행 {idx} URL 추출 실패: uid를 찾을 수 없음 (href: {href_value[:50]}, onclick: {onclick_value[:50]})")
                else:
                    print(f"⚠️ [TASK] 행 {idx} 링크 요소를 찾을 수 없음")
            except Exception as e:
                # 링크 추출 실패 시 빈 문자열 유지
                url = ""
                print(f"❌ [TASK] 링크 추출 실패 (행 {idx}): {type(e).__name__} - {str(e)[:50]}")

            # 데이터 검증
            if not all([status, title, teacher, date]):
                print(f"[TASK] 행 {idx}: 필수 데이터 누락 - 건너뛰기 (status='{status}', title='{title}', teacher='{teacher}', date='{date}')")
                continue

            # Post 딕셔너리 생성
            post = {
                "title": title,
                "link": url,  # URL 할당
                "teacher": teacher,
                "date": date,
            }
            
            # URL 저장 확인 로그
            print(f"📝 [TASK] 행 {idx} 저장: title='{title[:30]}...', link='{url[:60] if url else '없음'}...', status='{status}'")

            # 상태에 따라 분류
            if status == "알림":
                notice_html_list.append(post)
                print(f"  → 알림 리스트에 추가됨 (총 {len(notice_html_list)}개)")
            elif status == "제출":
                submit_html_list.append(post)
                print(f"  → 제출 리스트에 추가됨 (총 {len(submit_html_list)}개)")
            elif status == "마감":
                end_html_list.append(post)
                print(f"  → 마감 리스트에 추가됨 (총 {len(end_html_list)}개)")

        except Exception as e:
            # 구체적인 예외 정보 출력 (디버깅용)
            print(f"[TASK] 행 {idx} 처리 중 오류: {type(e).__name__} - {str(e)}")
            continue

    # 최종 결과 요약
    print(f"\n📊 수행평가 크롤링 완료:")
    print(f"  - 알림: {len(notice_html_list)}개")
    print(f"  - 제출: {len(submit_html_list)}개")
    print(f"  - 마감: {len(end_html_list)}개")
    print(f"  - 총계: {len(notice_html_list) + len(submit_html_list) + len(end_html_list)}개")
    
    driver.get(default_url)
    return notice_html_list, submit_html_list, end_html_list
