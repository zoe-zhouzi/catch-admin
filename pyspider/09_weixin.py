import sys
import json
import re
import time

import requests
from lxml import etree

import pymysql
import pymongo
import datetime

def spiderWeixin(url):
    result = {}
    res = requests.get(url)
    html = etree.HTML(res.content)
    # res.text返回的是Unicode类型的数据，而res.content返回的是bytes类型的数据。
    # etree解析是不支持编码声明的Unicode字符串的。
    is_error = html.xpath('//div[@class="weui-msg__text-area"]/div/text()')
    if len(is_error) != 0:
        result['code'] = 1
        result['msg'] = '页面显示' + is_error[0].strip()
        return result
    result['code'] = 0
    result['msg'] = ''
    result['url'] = url
    title = html.xpath('//h1/text()')[0].strip()
    author = html.xpath('//strong[@class="profile_nickname"]/text()')[0]

    text = html.xpath('//div[@id="js_content"]')[0].xpath('string(.)').strip()

    pub_time_x = re.findall('create_time.*?=.*?"(.*?)"', res.text)[0]
    time_local = time.localtime(int(pub_time_x))
    fakeid = re.findall('appuin.*?=.*?"".*?"(.*?)";', res.text)[0]
    if(len(fakeid)==0): 
        fakeid = re.findall('appuin.*?=.*?"(.*?)".*?;', res.text)[0]
    # print('fakeid', fakeid)

    # 转换成新的时间格式(精确到分)
    pub_time = time.strftime("%Y-%m-%d %H:%M", time_local)
    result['author'] = author
    result['source_article'] = {
        'url': url,
        'title': title,
        'publish_time': pub_time,
        'text': text
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'cookie': 'appmsglist_action_3909423749=card; RK=qb1ZhJEo5Z; ptcz=e8399a5dc8de63034290edf383a4caeb8de9f147785dcbe78be5b7a82e23d0e6; ua_id=sV6KsdxrJDmiIYEpAAAAACdgkyXbD295O7b61kTKHyE=; wxuin=83854208680654; mm_lang=zh_CN; pgv_pvid=2852576640; _t_qbtool_uid=aaaa0mlgdn8iqck55petse5wtj4q88cb; _ga=GA1.1.1942304335.1686023570; _ga_QL0HTHVWN7=GS1.1.1686026935.2.0.1686026935.0.0.0; uuid=d170c796b329033921190cff8edab56d; rand_info=CAESIECoqm5t8LJqdyBBB2CQH2VgbMQayZoLkQmoTaaqRKC4; slave_bizuin=3909423749; data_bizuin=3909423749; bizuin=3909423749; data_ticket=Vb+/ecSRxEcrK9Q4QV1hButHZbgS5EyQt2kIma4psVmonRCfYtevh8B6YEZDvWcq; slave_sid=TXRZb1dQUmFTTmZVdXRVbEJGYUlIY2J3cnY2T2xCV0VGSFNaeVM5RmlhdGY4MVBoNXlzZ2JkbFB1TXpoXzFTOGRKbExEbWJRUGUzeFVoemc2MERuZzNIOWs2UWZnOURzdEdacHNRaDBDamQ1MXliSHlTRzRqWHRERllrTmxKSXJrYTNTNldDM1BZZEczQURl; slave_user=gh_455fd071b105; xid=06192a0f4c027f94d07ff4c9713b7762; _clck=3909423749|1|fcq|0; _clsk=pa1c82|1687565275778|2|1|mp.weixin.qq.com/weheat-agent/payload/record'
    }
    # 微信公众号接口
    begin = 0
    links = []
    # 跟cookie一样登录后获取
    token = "1863570133"
    headers['Referer'] = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=1747456531&lang=zh_CN'
    while begin < 25:
        # 这个count也是变化的，绝了不同的公众号不一样
        article_urls = f'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin={begin}&count=5&fakeid={fakeid}&type=9&query=&token={token}&lang=zh_CN&f=json&ajax=1'
        # print(article_urls)
        res = requests.get(article_urls, headers=headers)
        # print(res.json())
        app_msg_list = res.json()['app_msg_list']
        for item in app_msg_list:
            links.append(item['link'])
        # 因为公众号提供的接口上面count的参数就是5，即使每页面返回6条数据count仍然显示5
        begin += 5
    # print(links)
    count = 0
    result['article_list'] = []
    for link in links:
        res = requests.get(link, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        })
        html = etree.HTML(res.content)
        if res.status_code == 200:
            title = html.xpath('//h1/text()')
            # 像这个url的内容就只有一个小程序的入口，没有啥意义
            if len(title) != 0:
                title = title[0].strip()
                text = html.xpath('//div[@id="js_content"]')[0].xpath('string(.)').strip()
                pub_time_x = re.findall('create_time.*?=.*?"(.*?)"', res.text)[0]
                time_local = time.localtime(int(pub_time_x))
                # 转换成新的时间格式(精确到分)
                pub_time = time.strftime("%Y-%m-%d %H:%M", time_local)
                result['article_list'].append({
                    'url': url,
                    'title': title,
                    'publish_time': pub_time,
                    'text': text
                })
                count = count + 1
                if count == 20:
                    break
        else:
            # print('微信公众号爬取出错了')
            break
    return result

# url = 'https://mp.weixin.qq.com/s/YZoMc8cfBIaEeMvJwqB9tw'

url = sys.stdin.read()

a = spiderWeixin(url)

if 'url' in a.keys():
    # mysql连接
    try:
        # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
        # # 定义一个指针
        # cursor = db.cursor()
        # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
        # cursor.execute(sql, (a['url'], '微信', json.dumps(a, ensure_ascii=False).encode('utf8')))
        # db.commit()
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "微信",
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

