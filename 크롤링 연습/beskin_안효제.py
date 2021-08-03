
import pandas as pd
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.select import Select



url = 'http://www.baskinrobbins.co.kr/store/map.php'
dv = webdriver.Chrome('chromedriver.exe')
dv.get(url)

try:
    WebDriverWait(dv,5).until( 
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'name'))) # 페이지 로딩 대기시간

except Exception as e:
    print('오류발생: ',e)

time.sleep(2)

result =[]
sido = dv.find_element_by_css_selector('select.location_1').find_elements_by_tag_name('option') # 시도 리스트 추출
for si in sido[1:]:
    sel_si = Select(dv.find_element_by_css_selector('select.location_1'))
    sel_si.select_by_value(si.text) # 드롭박스에서 시도 선택
    time.sleep(2)
    print(f'{si.text} 지역 매장 수집 시작 {sido.index(si)}/{len(sido)-1}')
    gu = dv.find_element_by_css_selector('select.location_2').find_elements_by_tag_name('option') # 시에 맞는 구군 리스트 추출
    for gun in gu[1:]:
        sel_gu = Select(dv.find_element_by_css_selector('select.location_2'))
        sel_gu.select_by_value(gun.text) # 드롭박스에서 구군 선택
        dv.find_element_by_css_selector('div.search > button').click() # 검색 버튼 클릭
        time.sleep(2)
        store_list = dv.find_elements_by_css_selector('div.scroll > ul >li') # 매장 리스트 추출
        print(f'{si.text} {gun.text} 매장위치 수집중 {gu.index(gun)}/{len(gu)-1}')
        time.sleep(2)
        for i in store_list: # 각 매장 데이터 추출
            stores = list(i.text.split('\n'))
            if len(stores) > 5:
                name = stores[1]
                address = stores[3]
                if 'favorite' in stores[4]: # 매장번호란에 스트ㄹㅇ 들어간 경우 예외
                    phone = ''
                else:
                    phone = stores[4]
                open_time = stores[5]
            else: # 정상적이지 않는 데이터 예외
                name = stores[0]
                address = si.text + gun.text
                phone = ''
                open_time = ''
            result.append([name]+[open_time]+[phone]+[address])
df = pd.DataFrame(result)
df.to_csv(f'전국베라 매장위치.csv')

dv.close()