import re
import time
import requests
from lxml import etree
from pymongo import MongoClient
from queue import Queue

import user_agent


start_url = 'https://www.lele36.com/'
ua = user_agent.get_ua()
client = MongoClient('mongodb://localhost:27017/')
lele_db = client['lele36']



header = {
    'User-Agent': ua
}

# proxy = {

# }

def get_first_chapter():
    first_res = requests.get(url=start_url,headers=header)
    first_res.encoding = 'utf-8'
    top_nav = etree.HTML(first_res.text)
    first_cha_urls = top_nav.xpath('//ul[@class="top-nav"]//li/a/@href')[1::]
    chapter_name = top_nav.xpath('//ul[@class="top-nav"]//li/a/text()')[1::]
    return first_cha_urls,chapter_name


def get_page(page_url):
    first_page = requests.get(url=page_url,headers=header)
    first_page.encoding = 'utf-8'
    re_page = r'<a .*-pg-(.*?).html" class="pagelink_a">尾页</a>'
    pages = int(re.findall(re_page,first_page.text)[0])
    page_html = etree.HTML(first_page.text)
    movies_url = page_html.xpath('//li[@class="p1 m1"]/a/@href')
    return movies_url,pages

def get_movies():
    first_cha_urls = get_first_chapter()[0]
    type_name = get_first_chapter()[1]
    for per in first_cha_urls:
        with open('{}'.format(type_name[first_cha_urls.index(per)]),'a') as file:
            lele_col = lele_db[type_name[first_cha_urls.index(per)]]
            movies = Queue()
            per_url = 'https://www.lele36.com' + per
            movies_url = get_page(per_url)[0]
            pages = get_page(per_url)[1]
            for movie in movies_url:
                movie_url = 'https://www.lele36.com' + movie
                file.write(movie_url)
                file.write('\n')
                movies.put(movie_url)
            for page in range(2,pages):
                print("{}{}".format(type_name[first_cha_urls.index(per)],page))
                next_page = 'https://www.lele36.com' + re.findall('(\?m\=vod-type-id-.*)\.html',per)[0] + '-pg-{}.html'.format(page)
                movies_url = get_page(next_page)[0]
                for movie in movies_url:
                    movie_url = 'https://www.lele36.com' + movie
                    file.write(movie_url)
                    file.write('\n')
                    movies.put(movie_url)
                time.sleep(1)
            while True:
                movie_item = {}
                detail_url = movies.get()
                print(detail_url)
                detail_res = requests.get(url=detail_url,headers=header)
                detail_res.encoding = 'utf-8'
                detail_html = etree.HTML(detail_res.text)
                movie_name  = detail_html.xpath('//dt[@class="name"]/text()')
                starring = detail_html.xpath('//div[@class="ct-c"]//dt[2]/a/text()')
                movie_type = detail_html.xpath('//div[@class="ct-c"]//dt[3]/a/text()')
                director = detail_html.xpath('//div[@class="ct-c"]//dd[1]/a/text()')
                area = detail_html.xpath('//div[@class="ct-c"]//dd[2]/a/text()')
                years = detail_html.xpath('//div[@class="ct-c"]//dd[3]/a/text()')
                language = detail_html.xpath('//div[@class="ct-c"]//dd[4]/a/text()')
                heat = detail_html.xpath('//div[@class="ct-c"]//dd[5]/text()')
                updata = detail_html.xpath('//div[@class="ct-c"]//dd[6]/text()')
                synopsis =  detail_html.xpath('//div[@name="ee"]//span/text()')

                movie_item['电影名称'] = movie_name[0]
                movie_item['主演'] = starring
                movie_item['类型'] = movie_type
                movie_item['导演'] = director
                movie_item['地区'] = area
                movie_item['年份'] = years
                movie_item['语言'] = language
                movie_item['热度'] = heat
                movie_item['更新日期'] = updata
                movie_item['剧情简介'] = synopsis
                lele_col.insert_one(movie_item)
                print('写入成功！')
                if movies.empty():
                    break
                time.sleep(3) 

def main():
    get_movies()
    

if __name__ == '__main__':
    main()