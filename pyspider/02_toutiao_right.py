import sys
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pymongo

import pymysql

def spiderToutiao(url):
    try:
        result = {}
        result["url"] = url

        chrome_options = Options()

        # chrome_options.add_argument("--headless")
        # 准备好参数配置
        option = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 谷歌浏览器去掉访问痕迹
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
        chrome_options.add_argument("--window-size=1920,1050")  # 专门应对无头浏览器中不能最大化屏幕的方案
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # chrome_options.headless = True
        # chrome_options.page_load_strategy = 'eager'
        # 初始化浏览器对象
        driver = webdriver.Chrome(options=chrome_options)
        # #  一个文章url
        driver.get(url)
        time.sleep(5)

        # 解析源文章
        # 标题
        title = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/h1').text
        # print(title)
        # 发布时间
        pub_time1 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/span[1]')
        pub_time2 = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/span[2]')
        if pub_time1.text[0].isdigit():
            pub_time = pub_time1.text
        else:
            pub_time = pub_time2.text
        # print(pub_time)
        # 文章内容
        article = driver.find_elements(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/article/p')
        # print('article', article)
        content = ''
        for a in article:
            content = content + a.text
        # print(content)

        # 用户主页url
        user_url_x = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[1]/div/div[1]/a[2]')
        user_url = user_url_x.get_attribute('href')
        # print(user_url)
        user_name = user_url_x.text
        # print(user_name)

        result["author"] = user_name
        result["source_article"] = {}
        result["source_article"]["url"] = url
        result["source_article"]["title"] = title
        result["source_article"]["publish_time"] = pub_time
        result["source_article"]["text"] = content


        # 进入用户主页
        # user_url = 'https://www.toutiao.com/c/user/token/MS4wLjABAAAA_HXqsrg9cXWGwzkNxp9gpS0mR3jd4FoUJ7Yc2HdJFwM/?source=tuwen_detail'
        driver.get(user_url)
        time.sleep(10)
        # 模拟滚动的
        js = 'window.scrollTo(0, document.body.scrollHeight)'
        # time.sleep(5)
        driver.execute_script(js)
        time.sleep(3)
        driver.execute_script(js)
        time.sleep(3)
        driver.execute_script(js)
        # 获取 url 列表
        lis = driver.find_elements(By.XPATH,'/html/body/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/div/div/div[2]/a')
        article_urls = []
        for li in lis:
            href = li.get_attribute("href")
            # 因为爬取的是全部的视频，因此视频里面可能有非文章的url，要去掉
            if re.findall('.*?article.*?', href):
                article_urls.append(href)
            # 设置1s的时候会让你输验证，不是安全秒数
            time.sleep(3)
        # print(article_urls)
        # print('list的长度', len(article_urls))

        result["article_list"] = []
        count = 0
        # 这里如果换一个新的浏览器窗口会不会验证会少一点，如果selenium的部署也能正常运转的话那就这样子做
        for url in article_urls:
            driver.get(url)
            # 解析源文章
            # 标题
            title = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/h1').text
            # print(title)
            # 发布时间
            pub_time1 = driver.find_element(By.XPATH,
                                            '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/span[1]')
            pub_time2 = driver.find_element(By.XPATH,
                                            '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/div/span[2]')
            if pub_time1.text[0].isdigit():
                pub_time = pub_time1.text
            else:
                pub_time = pub_time2.text
            # print(pub_time)
            # 文章内容
            article = driver.find_elements(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div/div/article/p')
            # print('article', article)
            content = ""
            for a in article:
                content = content + a.text
            # print(content)
            # 用户主页url
            user_url_x = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[3]/div[1]/div/div[1]/a[2]')
            user_url = user_url_x.get_attribute('href')
            # print(user_url)
            time.sleep(3)
            result["article_list"].append({
                "url": url,
                "title": title,
                "publish_time": pub_time,
                "text": content
            })
            count = count + 1
            if count == 20:
                break
        return result
    finally:
        driver.close()

# url = 'https://www.toutiao.com/article/7221035573425734196/?log_from=d84ace01f1e64_1681375102658'
# 接口来自node调用的参数
url = sys.stdin.read()

a = spiderToutiao(url)

try:
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password="2370917986.", db='osintcuc')
    # 定义一个指针
    cursor = db.cursor()
    sql = "insert into searchRes(url, source, data) values(%s, %s, %s)"
    cursor.execute(sql, (a['url'], '头条', json.dumps(a, ensure_ascii=False).encode('utf8')))
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
