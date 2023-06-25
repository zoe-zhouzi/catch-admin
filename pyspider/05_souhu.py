import sys
import json
import re

import requests
from lxml import etree
import pymysql
import pymongo
import datetime


# 文章列表可以直接访问
# url = 'https://www.sohu.com/a/500852881_531924'

def spiderSohu(url):
    # 用来存储请结果
    result = {}
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        # 'Origin': 'https://www.sohu.com/a/673691791_121284943?edtsign=C37C415B63E32FB7B37F527364D1DC28E4330618&edtcode=xW5WLWm834RlWgB9uxAiFw%3D%3D&scm=1103.plate:663:0.0.1_1.0&_f=index_cpc_1_0&spm=smpc.channel_258.block4_314_Y6ubu8_1_fd.17.1683525090875KphH29R_1090',
        # 'Referer': 'https://mp.sohu.com/profile?xpt=cHBhZzkzMTJkNmFiNmM1M0Bzb2h1LmNvbQ==&scm=1019.20005.0.0.0&spm=smpc.csrpage.suggest-list.1.16811150083899sCo9jX',
        'Content-Type': 'application/json;charset=utf-8',
        # 'Cookie': 'IPLOC=CN; gidinf=x099980107ee16eb9619b7431000e52e98d73cbcc37c; __qca=P0-1223873381-1682602030057; SUV=16826020318395k3g7e; _ga=GA1.1.1220740987.1682602112; __bid_n=187c2e6cf865a538aa4207; __gads=ID=f0dd0fda26251af3-22d90fc901e000cc:T=1682602030:S=ALNI_MYv28X3QUZ3bjI2SUJSjjqLSRjt4w; _ga_Q38L0DFY6G=GS1.1.1682602184.1.0.1682602692.0.0.0; cto_bundle=2wZipl8lMkJISXdCWG9NcmVrOTVicnBKVHdTbFU0WDVlb24xaDl3eERFVDZMVG0wbEFNTm9mRXhHcVJCRnRZTmpWMDdiUmduQ3FZajFHZk01ckE0alhHbHNGdVNMc050OGxReSUyQiUyQmpncnh5RHNEMWZCVnVjNDElMkZEZDFRRW9MZXVuNWFhdkp1dWpuWXEzcFhVRkROd2FvS2FTbmZqenlQVmcwcWdZYzRKRnh6Mm10V3Y4djlyJTJGWDVKN0piNXZzWXp4OU40SHNP; _ga_DFBWYFE6Q0=GS1.1.1682602115.1.1.1682603956.59.0.0; __gpi=UID=00000bfe3ac9f5f0:T=1682602030:RT=1682660496:S=ALNI_MY6iFZ8gQJWAVv-RNjErhhXun7Vdw; clt=1683525091; cld=20230508135131; reqtype=pc; FPTOKEN=hKDzD0dQCuZ3Iis2TSZzgdnU2B1aPOD6N47bnScVOEcCM8HIY0/k1d1fcJgUTkuR4L+WBSlZEFyvsTaPLimn5V2SvKOb17fhsfh+OnSQjV9efVX9JrVv10Y0Q9oSclW0JBxqqx9+7mOroTWfJLkwPsJUzJXswm/mvYu9DUSv2lJRnoI9AIQaP60wbvHaaFLnCLHscxFGdant2kk8yHkj/Zx7CZdHNhwKrH7/v9YGT7WPEsTaYQhiNxy34lymfzGb88YTcBgpbWHAW/CLNSjRAWto7cYjOFXatARJN9qsL93qMpIzcCn3wtQOOEoRdHAz+d7DwcvNZeozf9KbQXAV2siIJ5Gr8RJrDK3tdIxqNyrLFyyHbN2ojB8RdLW12sA3rlp2iFIkHmP0rKz0pWuy/Q==|KdmBqv6PMQXQk4a6klqf1uwdBNTKuygcIp49Wq3HBbo=|10|647676a19fc1f43a096c1c058fee7d51; t=1683525742135'
    }
    res = requests.get(url, headers=headers)
    html = etree.HTML(res.text)

    is_error = True if len(re.findall('404', res.text)) else False
    if is_error:
        result['code'] = 1
        result['msg'] = html.xpath('//title/text()')[0].strip()
        return result

    result['code'] = 0
    result['msg'] = ''
    result['url'] = url
    result['source_article'] = {}
    result['source_article']['url'] = url
    result['article_list'] = []
    # 标题
    # title = html.xpath('//h1/text()')[0].strip()
    title = html.xpath('//h1/text()')
    if len(title) == 0:
        title = html.xpath('//h3[@class="article-title"]/text()')
        if len(title) == 0:
            return result
    else:
        title = title[0].strip()

    result['source_article']['title'] = title
    # 发布时间
    pub_time = html.xpath('//span[@id="news-time"]/text()')[0]
    result['source_article']['publish_time'] = pub_time
    # 内容
    p_list = html.xpath('//*[@id="mp-editor"]/p/text()')
    content = ''
    for p in p_list:
        content = content + p
    result['source_article']['text'] = content
    # 用户url,获取mkey
    # class="abrosintcucd-article-author-card-author-info"
    author = html.xpath('//div[@id="user-info"]/h4/a/text()')[0].strip()
    result['author'] = author
    user_url = html.xpath('//div[@id="user-info"]/h4/a/@href')[0]
    user_page = requests.get(user_url, headers=headers)
    regex = re.compile(r',"mkey":"(.*?)",')
    mkey = re.findall(regex, user_page.text)[0]

    # 爬取用户最近20条文章
    # 这种方式挺方便，data里面对于不同的用户只需要修改mkey这个值，但是不知道这个值怎么获得
    count = 0
    params = {"suv": "16801545196676xah34", "pvId": "1681123243519_TvhswIo", "clientType": 3, "resourceParam": [
        {"requestId": "1681123243732_16801545196676_TDa", "resourceId": "1681123243732364725", "page": 1,
         "size": 20, "spm": "smpc.channel_248.block3_308_NDdFbm_1_fd",
         "context": {"pro": "0,1,3,4,5", "feedType": "XTOPIC_SYNTHETICAL", "mkey": mkey},
         "resProductParam": {"productId": 324, "productType": 13},
         "productParam": {"productId": 325, "productType": 13, "categoryId": 47, "mediaId": 1}, "expParam": {}}]}
    while True:
        article_url = 'https://cis.sohu.com/cisv4/feeds'
        res = requests.post(article_url, data=json.dumps(params), headers=headers)
        data_dict = res.json()  # dict
        a = ''
        for key in data_dict:
            a = key
        data = data_dict[a]

        base_url = 'https://www.sohu.com'
        for item in data['data']:
            article_url = base_url + item['resourceData']['contentData']['url'].split('?')[0]
            res = requests.get(article_url, headers=headers)
            # print(res.text)
            html = etree.HTML(res.text)
            # 标题
            # print(article_url)
            title = html.xpath('//div[@class="text-title"]/h1/text()')
            if len(title) == 0:
                title = html.xpath('//h3[@class="article-title"]/text()')[0].strip()
                pub_time = html.xpath('//span[@class="l time"]/text()')
                p_list = html.xpath('//div[@class="original-title"]/p/text()')
                content = ''
                for p in p_list:
                    content = content + p
            else:
                title = title[0].strip()
                # 发布时间
                pub_time = html.xpath('//span[@id="news-time"]/text()')[0]
                # 内容
                p_list = html.xpath('//*[@id="mp-editor"]/p/text()')
                # print(p_list)
                content = ''
                for p in p_list:
                    content = content + p
            result['article_list'].append({
                'url': article_url,
                'title': title,
                'publish_time': pub_time,
                'text': content
            })
            count = count + 1
            if count == 20:
                return result
        params['resourceParam'][0]['page'] += 1

def parse_article():
    pass

# 接口来自node调用的参数
url = sys.stdin.read()

a = spiderSohu(url)

if 'url' in a.keys():
    # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
    # cursor = db.cursor()
    # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
    # cursor.execute(sql, (a['url'], '搜狐', json.dumps(a, ensure_ascii=False).encode('utf8')))
    # db.commit()
    # # print('@@@@@@@')
    # cursor.close()
    # db.close()
    try:
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "搜狐",
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
        client.close()

    # try:
    #     db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
    #     # 定义一个指针
    #     cursor = db.cursor()
    #     sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
    #     cursor.execute(sql, (a['url'], '搜狐', json.dumps(a, ensure_ascii=False).encode('utf8')))
    #     db.commit()
    #     print('@@@@@@@')
    # except:
    #     pass
    # finally:
    #     cursor.close()
    #     db.close()

# 将字典编码为UTF-8格式的JSON字符串
# json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

# 将JSON字符串写入标准输出
# print(json_data.decode('utf8'))
print({})



# if a == 0:
#     # print({'a': 0})
#     json_data = json.dumps({"a": 0}, ensure_ascii=False).encode('utf8')
#     print(json_data.decode('utf8'))
# else:
#     try:
#         db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
#         # 定义一个指针
#         cursor = db.cursor()
#         sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
#         cursor.execute(sql, (a['url'], '搜狐', json.dumps(a, ensure_ascii=False).encode('utf8')))
#         db.commit()
#     except:
#         pass
#     finally:
#         cursor.close()
#         db.close()

#     # 将字典编码为UTF-8格式的JSON字符串
#     json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

#     # 将JSON字符串写入标准输出
#     print(json_data.decode('utf8'))

# try:
#     db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
#     # 定义一个指针
#     cursor = db.cursor()
#     sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
#     cursor.execute(sql, (a['url'], '搜狐', json.dumps(a, ensure_ascii=False).encode('utf8')))
#     db.commit()
# except:
#     pass
# finally:
#     cursor.close()
#     db.close()

# # 将字典编码为UTF-8格式的JSON字符串
# json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

# # 将JSON字符串写入标准输出
# print(json_data.decode('utf8'))