import sys
import json
import re

import requests
from lxml import etree
import pymysql
import pymongo
import datetime
import time


def spiderBilibili(url):
    result = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    res = requests.get(url, headers=headers)
    html = etree.HTML(res.text)

    is_error = True if len(re.findall(r'"error":\{"code":404', res.text)) else False
    if is_error:
        result['code'] = 1
        result['msg'] = html.xpath('//title/text()')[0].strip()
        return result

    result['code'] = 0
    result['msg'] = ''
    result['url'] = url

    media_type = '短视频'
    source = 'bilibili'
    # 作者
    author = html.xpath('//div[@class="up-detail-top"]/a/text()')[0].strip()
    # print(author)
    # 发布时间
    pub_time = html.xpath('//span[@class="pudate-text"]/text()')[0].strip()
    # print(pub_time)
    # 标题
    title = html.xpath('//h1[@class="video-title tit"]/text()')[0].strip()
    # print(title)
    # 用户主页
    user_url = "https:" + html.xpath('//div[@class="up-detail-top"]/a/@href')[0]
    # print(user_url)
    result['author'] = author
    result['source_article'] = {
        'url': url,
        'title': title,
        'publish_time': pub_time,
        'text': '-'
    }
    # mid = '344849038'
    mid = re.findall(r'https://space.bilibili.com/(\d+)', user_url)[0]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'referer': user_url,
    }
    # ajax请求，直接返回视频列表的json包，需要referer这个参数
    user_url = f'https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&pn=1&ps=25&index=1&order=pubdate&order_avoided=true&platform=web&web_location=1550101&w_rid=14e141ae835a95f990b25d8d6c9294d6&wts=1681897150'
    res = requests.get(user_url, headers=headers)
    data_dict = res.json()
    video_list = data_dict['data']['list']['vlist']
    count = 0
    result['article_list'] = []
    for video in video_list:
        timestamp = video['created']
        bvid = video['bvid']
        video_url = f'https://www.bilibili.com/video/{bvid}/'
        # 转换成localtime
        time_local = time.localtime(timestamp)
        # 转换成新的时间格式(精确到秒)
        pub_time = time.strftime("%Y-%m-%d %H:%M", time_local)
        title = video['title']
        result['article_list'].append({
            'url': video_url,
            'publish_time': pub_time,
            'title': title,
            'text': '-'
        })
        count = count + 1
        if count == 20:
            break
    return result

# url = 'https://www.bilibili.com/video/av516377527/'

# 接口来自node调用的参数
url = sys.stdin.read()

a = spiderBilibili(url)

if 'url' in a.keys():
    try:
        # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
        # # 定义一个指针
        # cursor = db.cursor()
        # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
        # cursor.execute(sql, (a['url'], 'bilibili', json.dumps(a, ensure_ascii=False).encode('utf8')))
        # db.commit()
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "哔哩哔哩",
            "excute_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "url": a['url'],
            "author": a['author'],
            "source_article": a['source_article'],
            "article_list": a['article_list'],
        }
        res = collection.insert_one(data)
    except:
        pass
    finally:
        # cursor.close()
        # db.close()
        client.close()

# 将字典编码为UTF-8格式的JSON字符串
json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

# 将JSON字符串写入标准输出
# print(json_data.decode('utf8'))
print({})