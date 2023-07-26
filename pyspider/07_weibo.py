import sys
import json
import re

import datetime
import requests
import pymysql
import redis
import pymongo

#  把爬取到的时间格式转换成 xxxx-xx-xx xx:xx:xxx
def handler_time(t):
    # 转换成 xxxx-xx-xx xx:xx:xxx 的datatime格式
    pub_time_x = datetime.datetime.strptime(t, "%a %b %d %H:%M:%S +0800 %Y")
    # 此时是一个 datatime 格式转换成 str 格式，不要最后的秒数
    pub_time = str(pub_time_x)[0:-3]
    return pub_time


# 文本处理
def handler_text(text):
    return re.sub(r'<.*?>', '', text).replace('\u200b', '')


# 如果 response 是json类型
def reqToJson(url):
    res = requests.get(url)
    return res.json()


def redisConn(host, port, db):
    # redis 连接
    redis_pool = redis.ConnectionPool(host=host, port=port, db=db)
    client = redis.Redis(connection_pool=redis_pool, decode_responses=True)
    return client


# 需要有一个每天自动获取cookie的方法，应该需要使用到selenium，这个必须要使用登录后的cookie才行，难道需要在这里直接写账号和密码
# 为啥麦公司的那个cookie永远都不失效
def getCookie():
    client = redisConn('172.17.33.149', 30467, 15)
    cookie = client.hget('Cookie', 'WB')
    return str(cookie, encoding='utf-8')


# 感觉需要每天生成cookie
def spiderWeibo(url):
    result = {}
    mblog_id = url.split('?')[0].split('/')[-1]
    uid = url.split('?')[0].split('/')[-2]
    # print(uid)
    # 一个ajax请求
    req_url = f'https://weibo.com/ajax/statuses/show?id={mblog_id}'

    data = reqToJson(req_url)
    # print(data)
    if data['ok'] == 0:
        result['code'] = 1
        result['msg'] = data['message']
        return result
    result['code'] = 0
    result['msg'] = ''
    result['url'] = url
    author = data['user']['screen_name']
    pub_time = handler_time(data['created_at'])
    title = handler_text(data['text'])
    text = handler_text(data['text'])

    result['author'] = author
    result['source_article'] = {
        'url': url,
        'title': title,
        'publish_time': pub_time,
        'text': text
    }

    user_url = f'https://weibo.com/u/{uid}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'referer': user_url,
    }
    cookies = {
        'SUB': '_2A25JnXNUDeRhGeNH41cT8yzKzz6IHXVq6-OcrDV8PUJbmtAGLWjTkW9NSm0Sti22enfSGEIte5xV3kGWZAhCD5IA',
        # 'SUB': getCookie()
    }

    result['article_list'] = []
    count = 0
    page = 1
    since_id = ''
    while True:
        article_urls = f'https://weibo.com/ajax/statuses/mymblog?uid={uid}&page={page}&feature=0' + (f'&since_id={since_id}' if since_id else '')
        # print(article_urls)
        res = requests.get(article_urls, headers=headers, cookies=cookies)
        # res = requests.get(article_urls, headers=headers)
        # print(res.text)
        temp = res.json()
        # 某页没有数据时，返回的结果是 {'ok':1}
        if 'data' in temp:
            article_list = temp['data']['list']
            since_id = temp['data']['since_id']
            # print(article_list)

            for article in article_list:
                user_id = article['idstr']
                mblog_id = article['mblogid']
                mblog_url = f'https://weibo.com/{user_id}/{mblog_id}'
                pub_time = handler_time(article['created_at'])
                title = handler_text(article['text'])
                text = handler_text(article['text'])
                result['article_list'].append({
                    'url': mblog_url,
                    'publish_time': pub_time,
                    'title': title,
                    'text': text
                })
                count = count + 1
                if count == 20:
                    break
            if count == 20:
                break
            page = page + 1
    return result


# url = 'https://weibo.com/1703659027/M9ZzSzk4v'

# 接口来自node调用的参数
url = sys.stdin.read()

a = spiderWeibo(url)

if 'url' in a.keys():
    try:
        # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
        # # 定义一个指针
        # cursor = db.cursor()
        # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
        # cursor.execute(sql, (a['url'], '微博', json.dumps(a, ensure_ascii=False).encode('utf8')))
        # db.commit()
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "微博",
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
# json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

# 将JSON字符串写入标准输出
# print(json_data.decode('utf8'))
print({})