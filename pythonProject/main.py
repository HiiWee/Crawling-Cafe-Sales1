import datetime
import time
import random
import pandas as pd
from IPython.display import display

import pyperclip
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 크롬 웹 드라이버의 경로를 설정!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
driverLoc = ""
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 브라우저 숨기기
driver = webdriver.Chrome(driverLoc, options=options)

# 네이버 로그인 페이지 접속
driver.get("https://nid.naver.com/nidlogin.login")

# 로그인 정보!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
login = {"id" : ""   # 네이버 아이디
        ,"pw" : ""   # 네이버 비밀번호
        }

# 로그인 정보 입력 함수
def clipboard_input(user_xpath, user_input):
    temp_user_input = pyperclip.paste()

    pyperclip.copy(user_input)
    driver.find_element_by_xpath(user_xpath).click()
    # 33333333333333333333333333333 OSX : COMMAND,  windowOS : CONTROL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ActionChains(driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()

    pyperclip.copy(temp_user_input)
    time.sleep(1)

# id, pw 입력 후 클릭
clipboard_input('//*[@id="id"]', login.get("id"))
clipboard_input('//*[@id="pw"]', login.get("pw"))
driver.find_element_by_xpath('//*[@id="log.login"]').click()

time.sleep(1)



# 결과 저장 경로
# 444444444444444444444444444444 수집값 저장경론 (경로만 저장하면됨)!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
save_path = "PycharmProjects/save/"

# 카페 정보
# 55555555555555555555555555555555555순서대로 입력하면 됨 이름은 임의로 지정 가능
cafe = {'name': ''                         # 카페 이름 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
       ,'page_link': '' }# 주소 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 777777777777777777777777777777777777777777777777
cafe.update({"keywords" : [""]})         # 검색 키워드 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

for keyword in cafe.get("keywords"):
    ### 카페 주소 입력
    driver.get(cafe.get("page_link"))

    ### 키워드 검색
    clipboard_input('//*[@id="topLayerQueryInput"]', keyword)
    try:
        driver.find_element_by_xpath('//*[@id="cafe-search"]/form/button').click()  # 왼쪽에 검색창
    except:
        driver.find_element_by_xpath('//*[@id="info-search"]/form/button').click()  # 오른쪽에 검색창

    # driver 객체가 get(url)로 요청한 페이지 내용들이 모두 로딩이 완료될 때까지 int(초) 만큼 암묵적으로 기다리게 하는 것이다.
    driver.implicitly_wait(0.5)
    # iframe 페이지로 전환하기 위해서는 다음의 코드가 필요합니다.
    driver.switch_to.frame('cafe_main')

    ### 키워드 수집 정보
    num_per_page = 15  # 페이지당 게시글 갯수(default: 15개)

    address_list = []
    page = 1

    l = True
    while l:

        time.sleep(random.randint(0, 5))

        ### 현재 페이지의 html 불러오기
        r = driver.page_source
        page_html = BeautifulSoup(r, "html.parser")
        content = page_html.find("div", class_="article-board result-board m-tcol-c").find('tbody')
        #         content = page_html.find_all("div", class_="article-board m-tcol-c")[1].find('tbody')
        body = content.find_all("tr")

        ### 게시글 정보 저장하기
        for x in body:
            temp_dict = {}
            if x.find("div", class_="board-number") is not None:
                temp_dict['no'] = x.find("div", class_="board-number").text.strip()
                temp_dict['title'] = x.find("div", class_="board-list").text.strip().replace('  ', '').replace('\n', '')
                temp_dict['link'] = x.find('a').get('href')
                temp_dict['name'] = x.find("td", class_="td_name").find('a', class_='m-tcol-c').text.strip()
                temp_dict['date'] = x.find("td", class_="td_date").text.strip()
                temp_dict['view'] = x.find("td", class_="td_view").text.strip()
                address_list.append(temp_dict)
        print("(현재시각) " + str(datetime.datetime.now()) + ": " + str(page) + "page done")

        ### 다음 페이지로 넘어가기
        page += 1
        driver.implicitly_wait(1)
        try:
            if page <= 10:  # 1~10 : 페이지 번호 그대로
                page_xpath = str(page)
                driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[' + page_xpath + ']').click()
            elif page == 11:  # 11 : 다음 버튼
                driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[11]/span').click()
            elif page > 11 and page % 10 != 1:  # 12~ : 페이지 번호 마지막 자리 + 1
                page_xpath = str(page - ((page - 1) // 10) * 10 + 1)
                driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[' + page_xpath + ']').click()
            elif page % 10 == 1:  # 21,31.. : 다음 버튼
                driver.find_element_by_xpath('//*[@id="main-area"]/div[7]/a[12]/span').click()
        except:
            address_df = pd.DataFrame(address_list)
            address_df['idx_no'] = range(1, len(address_df) + 1)  # 조인할 키 값
            address_df.to_html(save_path + "cafe_address_" + cafe.get("name") + "_" + keyword + ".pkl")
            print("(현재시각) " + str(datetime.datetime.now()) + ": done")
            l = False

if len(set(address_df['no'])) != len(address_df):
    print("게시글 번호에 중복 존재")
print("검색게시글수 : ", address_df.shape)
display(address_df.head())