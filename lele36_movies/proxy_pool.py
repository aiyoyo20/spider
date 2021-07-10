import requests
from lxml import etree
import random
from user_agent import get_ua
import time

header = {
    'user-agent': get_ua()
}
def get_proxies():
    pro_list = list()
    for page in range(1,50):
        print(page)
        page_url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
        page_res = requests.get(url=page_url,headers=header)
        page_res.encoding = 'utf-8'
        page_html = etree.HTML(page_res.text)
        data = page_html.xpath('//tr//td/text()')
        for pe in range(15):
            ip = data[0 + 7*pe]
            port = data[1 + 7*pe]
            pro = ip + ':' + port
            pro_list.append(pro)
        time.sleep(3)
    return pro_list

def test_proxies(*pro_list):
    great_pro = list()
    pro_list = pro_list
    for per in pro_list:
        proxy = {
             "http": "http://{}".format(per), 
             "https": "http://{}".format(per), 
        }
        try:
            test_res = requests.get(url='http://ip.chinaz.com/',headers=header,proxies=proxy,timeout=(5,5))
            great_pro.append(per)
        except:
            print('error')
    print(great_pro)
    return great_pro




def my_proxies():
    pass