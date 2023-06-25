import sys
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import pymysql
import pymongo

def spiderBaijiahao(url):
    try:
        result = {}
        result['url'] = url

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # driver = webdriver.Chrome(options=chrome_options)

        chrome_options = webdriver.ChromeOptions()
        # 准备好参数配置
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('log-level=3')
        # chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 谷歌浏览器去掉访问痕迹
        # chrome_options.add_argument(
        #     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
        # chrome_options.add_argument("--window-size=1920,1050")  # 专门应对无头浏览器中不能最大化屏幕的方案
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(15)

        # 用户名
        author = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[2]/a/p').text
        # 发布时间
        pub_time = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[2]/div/span[1]').text
        # print(pub_time)
        # 标题
        title = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[1]').text
        # print(title)
        # 文本
        ps = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/p')
        content = ''
        for p in ps:
            content = content + p.text
        # print(content)
        result['author'] = author
        result['source_article'] = {}
        result['source_article']['url'] = url
        result['source_article']['title'] = title
        result['source_article']['publish_time'] = pub_time
        result['source_article']['text'] = content

        # 用户主页
        author_url = driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[2]/a').get_attribute('href')
        driver.close()
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(author_url)
        # # document.body.scrollHeight 是用来获取滚动条的高度
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        time.sleep(5)
        driver.execute_script(js)
        time.sleep(5)
        driver.execute_script(js)
        time.sleep(5)
        driver.execute_script(js)
        time.sleep(5)

        # 定位到链接元素
        links = driver.find_elements(By.XPATH, '/html/body/div[2]/div/div[4]/div[1]/div[1]/div/div[2]/div/div[1]/div/div/div/div')

        article_list = []
        regex = 'https://baijiahao.baidu.com/s\?id=(.*?)'
        for item in links:
            link = item.get_attribute('url')
            if link is None:
                break
            isArticle = len(re.findall(regex, link))
            if isArticle != 0:
                article_list.append(link)
        # print(article_list)
        # 只获取最新的20条新闻
        count = 0
        result['article_list'] = []
        for article_url in article_list:
            driver.get(article_url)
            time.sleep(5)
            # 发布时间
            pub_time = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[2]/div/span[1]').text
            # print(pub_time)
            # 标题
            title = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div/div[1]').text
            # print(title)
            # 文本
            ps = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/p')
            content = ''
            for p in ps:
                content = content + p.text
            # print(content)
            result['article_list'].append({
                'url': article_url,
                'title': title,
                'publish_time': pub_time,
                'text': content
            })
            count = count + 1
            if count == 20:
                break
        return result
    finally:
        driver.close()
        # pass

# url = 'https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9796763631185219618%22%7D&n_type=-1&p_from=-1'
url = sys.stdin.read()

a = spiderBaijiahao(url)

try:
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
    # 定义一个指针
    cursor = db.cursor()
    sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
    cursor.execute(sql, (a['url'], '百家号', json.dumps(a, ensure_ascii=False).encode('utf8')))
    db.commit()
except:
    pass
finally:
    cursor.close()
    db.close()


# 将字典编码为UTF-8格式的JSON字符串
json_data = json.dumps(a, ensure_ascii=False).encode('utf8')

# 将JSON字符串写入标准输出
print(json_data.decode('utf8'))
