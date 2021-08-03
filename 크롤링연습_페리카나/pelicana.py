

import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from itertools import count
import datetime
import ssl


result = []
for i in range(2):
    url = f'https://pelicana.co.kr/store/stroe_search.html?page={i+1}&branch_name=&gu=&si='
    context = ssl._create_unverified_context()
    # ret = get_req_url(url)
    req = urllib.request.Request(url) 
    try: 
        response = urllib.request.urlopen(req, context=context)
        if response.getcode()==200:
            print("[%s] URL Request success" % datetime.datetime.now())
            try:
                rcv = response.read()
                ret = rcv.decode('utf-8')
            except UnicodeDecodeError:
                ret = rcv.decode('utf-8', 'replace')
    except Exception as e:
        print(e)
        print("[%s] Error For URL" % datetime.datetime.now())

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
        break

df = pd.DataFrame(result[:-1], columns=('store', 'sido','gu','address','phone'))
df.to_csv('./Lec08/test/페리카나 매장주소.csv')