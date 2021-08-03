import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from itertools import count
import datetime
import ssl

def get_req_url(url, enc='utf-8'):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            print(f'[{datetime.datetime.now()}] Success')
            try:
                rcv = response.read()
                ret = rcv.decode(enc)
            except UnicodeDecodeError:
                ret = rcv.decode(enc, 'replace')
            return ret
    except Exception as e:
        print(e)
        print(f"[{datetime.datetime.now()}] Error for URL: url")
        return None


def get_pelicana(result):
    for i in range(1):
        url = f'https://pelicana.co.kr/store/stroe_search.html?page={i+1}&branch_name=&gu=&si='
        ret = get_req_url(url)
        html = BeautifulSoup(ret, 'html.parser')
        data = html.find('table', class_="table mt20")      
        data_tbody = data.find('tbody')       
        data_tbody_tr = data_tbody.find_all('tr')
        bEnd = True
        print(f'페리카나 매장 크롤링:', i)
        for i in data_tbody_tr:
            bEnd =False
            store = list(i.strings)
            name = store[1]
            address = store[3]
            phone =store[5].strip()
            sido_gu = address.split()[:2]
            result.append([name]+sido_gu+[address]+ [phone])
        
        if bEnd == True:
            return
    return


        
def get_cheo(): # 각자 파일 생성
    url ='http://www.cheogajip.co.kr/bbs/board.php?bo_table=store'
    ret = get_req_url(url)
    html = BeautifulSoup(ret, 'html.parser')
    # data = html.find('nav', id='bo_cate')
    # data_ul = data.find('ul')
    sido = html.find("nav", id='bo_cate').find_all("li")[1:]
    for href in sido:
        big_url = href.find("a")["href"]
        map = href.find('a').text
        bEnd =True
        result = []
        for i in count():
            url =f'{big_url}&page={i+1}'
            context = ssl._create_unverified_context()
            ret = get_req_url(url)
            html = BeautifulSoup(ret, 'html.parser')
            data = html.find('div', class_='tbl_head01 tbl_wrap')
            data_tbody = data.find('tbody')
            data_tbody_tr = data_tbody.find_all('tr')
            aEnd = True
            print(f'처갓집 매장 크롤링: {map}{i+1}페이지')
            for i in data_tbody_tr:
                bEnd = False
                store = list(i.strings)
                if len(store) > 8:
                    name = store[3]
                    address = store[5]
                    phone =store[7]
                    sido_gu = address.split()[:2]
                    result.append([name]+[' '.join(sido_gu)]+[address]+ [phone])
                else:
                    aEnd = False
                    break
            if aEnd == False:
                df = pd.DataFrame(result, columns=('지점', '지역','주소','전화번호'))
                df.to_csv(f'./test/처갓집 {map} 매장주소.csv')
                break
        if bEnd == True:
            return          
    return

def get_cheo_total(result): # 통합 파일 생성
        for i in count():
            url =f'http://www.cheogajip.co.kr/bbs/board.php?bo_table=store&page={i+1}'
            context = ssl._create_unverified_context()
            ret = get_req_url(url)
            html = BeautifulSoup(ret, 'html.parser')
            data = html.find('div', class_='tbl_head01 tbl_wrap')
            data_tbody = data.find('tbody')
            data_tbody_tr = data_tbody.find_all('tr')
            bEnd =True
            print(f'처갓집 매장 크롤링: {i+1}페이지')
            for i in data_tbody_tr:
                bEnd = False
                store = list(i.strings)
                if len(store) > 8:
                    name = store[3]
                    address = store[5]
                    phone =store[7]
                    sido_gu = address.split()[:2]
                    result.append([name]+[' '.join(sido_gu)]+[address]+ [phone])
                else:
                    return
            if bEnd == True:
                return
        return




if __name__ == '__main__':
    # result = []
    # print('페리카나 매장 크롤링 시작')
    # get_pelicana(result)
    # df = pd.DataFrame(result[:-1], columns=('store', 'sido','gu','address','phone'))
    # df.to_csv('./Lec08/test/페리카나 매장주소.csv')
    # print('페리카나 매장 크롤링 완료')
    print('처갓집 매장 크롤링 시작')
    get_cheo()
    result = []
    get_cheo_total()
    df = pd.DataFrame(result, columns=('지점', '지역','주소','전화번호'))
    df.to_csv('./test/처갓집 매장주소.csv')

    print('처갓집 매장 크롤링 완료')

