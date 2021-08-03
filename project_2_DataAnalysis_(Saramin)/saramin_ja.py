import pandas as pd
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
from selenium.webdriver import ActionChains

# ================================사용자 직접 검색 시 필요=====================================

# search_data = input('검색어를 입력해주세요: ') # 사용자한테 검색어 받을 경우 활성화

# ================================= 검색 진행 ================================================

url = 'https://www.saramin.co.kr/zf_user/' # 메인페이지
driver = webdriver.Chrome('chromedriver.exe')
driver.get(url) # 메인페이지 호출

try:
    WebDriverWait(driver,5).until(
        EC.presence_of_all_elements_located((By.ID, 'search_open'))) # 메인페이지 로딩 대기 - 검색창

except Exception as e:
    print(e, '페이지 로딩시간 초과')
    driver.close()

time.sleep(1)
driver.find_element_by_id('search_open').click() # 검색창 활성화
driver.find_element_by_id('ipt_keyword_recruit').clear() # 검색창 기본문구 제거

# driver.find_element_by_id('ipt_keyword_recruit').send_keys(search_data) # 검색값 입력 (사용자 직접 검색 시 필요)

time.sleep(1)
search_key = '자바'
driver.find_element_by_id('ipt_keyword_recruit').send_keys(search_key) # 검색 key 전달
driver.find_element_by_css_selector('button#btn_search_recruit').click() # 검색버튼 클릭

# ================================= 검색 완료 후 페이지 로딩 및 채용정보 유무 확인 ==============

try:
    WebDriverWait(driver,5).until(
        EC.presence_of_all_elements_located((By.ID, 'recruit_info_list'))) # 검색페이지 로딩 대기
    error = ' '
except Exception as e:
    error = f'{search_key}(으)로 수집할 채용정보가 없습니다.'
    print(error)

time.sleep(1)

if '채용정보' in error: # 채용정보가 없는 경우 에러처리
    pass
else:
    try:
        driver.find_element_by_css_selector('#content > ul.tab_search_result.on > li:nth-child(2) > a').click() # 채용정보탭 클릭

    except NoSuchElementException as e:
        print(f'{search_key}(으)로 수집할 채용정보가 없습니다.')



    # ===================================채용 정보 총 건수 추출===============================================

    time.sleep(2)
    try:
        total = int(driver.find_element_by_css_selector('span.cnt_result').text[2:-1].replace(',','')) # 검색 총 채용정보 건수 추출
        total_page = math.ceil(total/40) # 총페이지수 추출 (총 채용정보 건수 / 채용정보 표현갯수)
        
        # ===================================크롤링 시작==============================================

        try:
            result = [] # 저장될 곳 초기화
            jobs_num = 0
            print(f'{"="*10} {search_key} 채용정보 수집시작 {"="*10}')
            for page in range(1,total_page+1): # 페이지수 자동 변경
                if page != 1: # 2페이지부터 수집
                    driver.find_element_by_xpath(f'//a[@page={page}]').click()
                time.sleep(2)
                
                jobs = driver.find_elements_by_css_selector('#recruit_info_list .item_recruit') # 채용정보 리스트 추출
                jobs_num += len(jobs)
                
                print(f'{page} 페이지 수집중 [{page}/{total_page}][총 {jobs_num}개 수집]') # 진행 상황표시  {round(((page)/total_page),3)*100}%
                for i in jobs:
                    title = i.find_element_by_css_selector('h2.job_tit').text # 채용정보 제목 추출
                    title_ = i.find_element_by_css_selector('h2.job_tit')
                    career = list(i.find_element_by_css_selector('div.job_condition').text.split('\n'))[1].replace('↑','') # 경력여부
                    station = list(i.find_element_by_css_selector('div.job_condition').text.split('\n'))[0] # 지역명 추출
                    date = i.find_element_by_css_selector('span.date').text.replace('~','') # 채용일시 추출
                    company = i.find_element_by_css_selector('div.area_corp a.data_layer').text # 회사명 추출
                    link = i.find_element_by_css_selector('a.data_layer').get_attribute('href') # 채용링크 추출
                    work_lst = i.find_elements_by_css_selector('div.job_sector a')
                    work_lst_2 = []
                    for work in work_lst: # 직종데이터 분리                        
                        work_lst_2.append(work.text)
                    machul = i.find_element_by_css_selector('div.area_corp_info') # 기업정보 탐색
                    ActionChains(driver).move_to_element(machul).perform() # 기업정보 요소 마우스오버
                    lst = [] # 매출액 초기화
                    lst_1 = []# 기업주소 초기화
                    machul_lst = machul.find_elements_by_css_selector('div.area_btn table > tbody > tr') # 기업정보 저장
                    for i in machul_lst: # 매출액, 기업주소 추출
                        if '매출액' in i.text:
                            i = i.text.split()
                            for won in i:
                                if '억' in won or '만원' in won: # (몇년도 기준) 제거
                                    lst.append(won)

                        elif '주소' in i.text: 
                            i = i.text.split()
                            for gu in i:
                                if '구' in gu and i.index(gu)!=1: # 구단위까지만 저장
                                    lst_1.append(i[1:i.index(gu)+1])
                                    break                        
                        else:
                            pass      
                    time.sleep(0.1)    
                    ActionChains(driver).move_to_element(title_).perform() # 기업정보 요소 마우스오버 초기화
                    
                    
                    if len(lst) !=0 and len(lst_1) !=0:
                        result.append([title]+[station]+[date]+[company]+[link]+[career]  # 결과값 저장
                        + [','.join(work_lst_2)] + [' '.join(lst)] + [' '.join(lst_1[0])] + [search_key])
                    elif len(lst) ==0 and len(lst_1) !=0:
                        result.append([title]+[station]+[date]+[company]+[link]+[career]  # 결과값 저장
                        + [','.join(work_lst_2)] + ['매출액없음'] + [' '.join(lst_1[0])] + [search_key])
                    elif len(lst) !=0 and len(lst_1) ==0:
                        result.append([title]+[station]+[date]+[company]+[link]+[career]  # 결과값 저장
                        + [','.join(work_lst_2)] + [' '.join(lst)] + [('주소없음')] + [search_key])
            print(f'{"="*10} {search_key} 채용정보 수집완료 {"="*10}')

        # ===================================크롤링 완료 후 파일 저장==============================================

####################csv 저장
            df = pd.DataFrame(result, columns=('title','station','date',
            'company','link','carrer', 'work', 'machul', 'juso', 'search_key'))
            df.to_csv(f'{search_key}_saramin_copy.csv')


####################DB 저장
            # db = SaramDB()
            # db.saram_drop()
            # db.saram_create()
            # for i in result:
            #     db.saram_insert(i[0],i[1],i[2],i[3])
            # db.db_free()
            # driver.close()
        except PermissionError as e:
            print(f'{search_key}_saramin.csv 이 열려있습니다. 닫고 다시 수집하세요.') # 파일이 열려있는 경우 에러처리


    except InvalidSessionIdException as e:
        print(f'{search_key}(으)로 등록된 채용정보가 없습니다.')