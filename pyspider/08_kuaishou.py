import sys
import json
import re
import time
import requests
import pymysql
import pymongo
import datetime

def timestampTransfrom(timestamp):
    # 转换成新的时间格式(精确到秒)
    t = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(timestamp) / 1000))
    return t

def spdierKuaishou(url):
    result = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Referer': 'https://www.kuaishou.com/short-video/3x75kngbkwa7ivs',
        'Cookie': 'did=web_1aa353938251a9b163241280b0821703; didv=1683854040165; _bl_uid=02lOqhqtjh4vXg7kqx4O6Cww3ekU; kpf=PC_WEB; clientid=3; userId=3247826112; kpn=KUAISHOU_VISION; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABtDH2Ds85DYaE6UJO3rMER0pLckDloQRoN1Wmo14XB5otX9WCjQueRpEdEVNOXVKHgP5JCNzrNGJXjZaIIBf07F-uWiqjt8tF3eZMiqPbnWI5whOXC5WIKiceYoDLj0ycdVgK8GQpoMzXUj-WraGWbgy5Z_NRcmjIm4qLVHc1z6jbizOyB0y-vezlvLGJzel4FrSvPLTmPjnxZEWLOdIDeBoSsguEA2pmac6i3oLJsA9rNwKEIiBubCgELjDG2j6JDWHcjIpE6uj32-U26ng88qKo9hKjBSgFMAE; kuaishou.server.web_ph=e444ec1a2025aa69a3e6ff48fa6e8eaa54ec',
    }

    res = requests.get(url, headers=headers)
    # print(res.text)
    # 异常处理，等有异常url再加异常处理
    # if xxxx:
    #     result['code'] = 1
    #     result['msg'] = '404找不到'
    #     return result
    result['code'] = 0
    result['msg'] = ''
    result['url'] = url
    a = re.findall('<script>window.__APOLLO_STATE__=(.*?);</script>', res.text)[0]
    # 发布时间
    pub_time_x = re.findall('"timestamp":.*?(\d+)', a)[0]
    pub_time = timestampTransfrom(pub_time_x)
    # 作者
    author = re.findall('"name":.*?"(.*?)"', a)[0]
    # title
    title = re.findall('"caption":.*?"(.*?)"', a)[0].replace('\\n', '')
    result['author'] = author
    result['source_article'] = {
        'url': url,
        'title': title,
        'publish_time': pub_time,
        'text': title
    }

    # 可以直接取url中的user_id
    user_id = url.split('/')[-1].split('?')[0]
    # 取在页面源码中找user_id
    # user_id = ''
    # user_ids = re.findall('"id":.*?"(.*?)".*?"name":', a)
    # for user_id in user_ids:
    #     if len(user_id) == 15:
    #         print(user_id)
    #         break

    user_url = f'https://www.kuaishou.com/profile/{user_id}'
    headers['Referer'] = user_url
    headers['content-type'] = 'application/json'
    video_urls = 'https://www.kuaishou.com/graphql'
    data = {"operationName": "visionProfilePhotoList",
            "variables": {"userId": "3xkgutgnipnakyu", "pcursor": "", "page": "profile"},
            "query": "fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  originCaption\n  likeCount\n  viewCount\n  commentCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  musicBlocked\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  tags {\n    type\n    name\n    __typename\n  }\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"}
    video_info = requests.post(video_urls, data=json.dumps(data), headers=headers)
    video_list = video_info.json()['data']['visionProfilePhotoList']['feeds']
    result['article_list'] = []
    count = 0
    for video in video_list:
        video_id = video['photo']['id']
        video_url = f'https://www.kuaishou.com/short-video/{video_id}?authorId={user_id}'
        title = video['photo']['originCaption'].replace('\n', '')
        # 发布时间
        pub_time_x = video['photo']['timestamp']
        pub_time = timestampTransfrom(pub_time_x)
        result['article_list'].append({
            'url': url,
            'title': title,
            'publish_time': pub_time,
            'text': title
        })
        count = count + 1
        if count == 20:
            break
    return result


# url = 'https://www.kuaishou.com/short-video/3x75kngbkwa7ivs'

url = sys.stdin.read()

a = spdierKuaishou(url)

if 'url' in a.keys():
    try:
        # db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
        # # 定义一个指针
        # cursor = db.cursor()
        # sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
        # cursor.execute(sql, (a['url'], '快手', json.dumps(a, ensure_ascii=False).encode('utf8')))
        # db.commit()
        client = pymongo.MongoClient("mongodb://172.17.33.149:32017")
        db = client["cucosint"]
        collection = db["searchres"]
        collection.create_index([('url', 1)], unique=True)
        data = {
            "source": "快手",
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