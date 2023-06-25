import sys
import json
import re

import requests
from lxml import etree
import pymysql
import pymongo
import datetime

def spiderWangyi(url):
    result = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Referer': 'https://www.163.com/',
    }

    # 判断一下url类型，如果是移动端的就把其转换成pc端的，因为移动端的网页进不去用户主页，只有pc端的可以
    # "https://c.m.163.com/news/a/HJG2ME8C0548GUNP.html"
    # 'https://www.163.com/dy/article/HJG2ME8C0548GUNP.html'
    if len(re.findall('https://(.*?).163.com/', url)) == 1:
        url = "https://www.163.com/dy/article/" + url.split('/')[-1]
        # result['code'] = 1
        # result['msg'] = '目前还未进行网易移动端网页解析'
        # return result

    # 需要加上 Referer 参数， 你的目标地址正确，但却没有得到你想要的页面，这就是妥妥的 反盗链。
    res = requests.get(url, headers=headers)
    html = etree.HTML(res.text)

    # 如果是 //www.163.com/news/article/ 中间是news的时候，表示一般来源是其他新闻网站
    if len(re.findall("https://www.163.com/news/article/(.*?).html", url)) == 1:
        result['code'] = 1
        result['msg'] = '访问不到作者号'
        return result
    if len(re.findall("https://www.163.com/sports/article/(.*?).html", url)) == 1:
        result['code'] = 1
        result['msg'] = '访问不到作者号'
        return result

    is_error = True if len(re.findall('wrap_2018_404', res.text))!=0 else False
    if is_error:
        result['code'] = 1
        result['msg'] = html.xpath('//title/text()')[0].strip()
        return result

    result['code'] = 0
    result['msg'] = ''
    result['url'] = url

    # 标题
    title = html.xpath('//h1[@class="post_title"]/text()')
    if len(title) == 0:
        return 0
    else:
        title = title[0]
    # print(title)
    # 发布时间
    pub_time = html.xpath('//div[@class="post_info"]/text()')[0].strip()[0:16]
    # print(pub_time)

    # 内容
    content_list = html.xpath('//div[@class="post_body"]/p/text()')
    # print(content_list)
    text = ''
    for c in content_list:
        text = text + c
    # print(text)
    author = html.xpath('//div[@class="post_wemedia_name"]/a/text()')[0]
    result['author'] = author

    result['source_article'] = {}
    result['source_article']['url'] = url
    result['source_article']['title'] = title
    result['source_article']['publish_time'] = pub_time
    result['source_article']['text'] = text

    # 从文章页面跳转到用户页面
    user_url = html.xpath('//div[@class="post_wemedia_avatar"]/a/@href')[0]
    res = requests.get(user_url, headers=headers)
    html = etree.HTML(res.text)
    article_urls = html.xpath('//ul[@class="list_box"]/li/a/@href')

    # 遍历文章列表，爬取文章列表的信息
    count = 0
    result['article_list'] = []
    for article_url in article_urls:
        res = requests.get(article_url, headers=headers)
        html = etree.HTML(res.text)
        # 标题
        title = html.xpath('//h1[@class="post_title"]/text()')[0]
        # print(title)

        # 发布时间
        pub_time = html.xpath('//div[@class="post_info"]/text()')[0].strip()[0:16]
        # print(pub_time)

        # 内容
        content_list = html.xpath('//div[@class="post_body"]/p/text()')
        # print(content_list)
        text = ''
        for c in content_list:
            text = text + c
        # print(text)
        result['article_list'].append({
            'url': article_url,
            'title': title,
            'publish_time': pub_time,
            'text': text
        })
        count = count + 1
        if count == 20:
            break
    return result

# url = 'https://www.163.com/dy/article/I2G2QAR40519DFFO.html'
# 接收来自node调用的参数
url = sys.stdin.read()
a = spiderWangyi(url)

if 'url' in a.keys():
    try:
        # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
        # # 定义一个指针
        # cursor = db.cursor()
        # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
        # cursor.execute(sql, (a['url'], '网易', json.dumps(a, ensure_ascii=False).encode('utf8')))
        # db.commit()
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "网易",
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