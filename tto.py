import json
from datetime import datetime, date
from bs4 import BeautifulSoup
import requests
import html
import mysql.connector
import ast
import time


# localhost
HOST = "localhost"
USERNAME = "root"
PASSWORD = "Aa@123456"
DATABASE = "datatrends"
ARTICLES_PER_LOAD = 16
DELETE_AFTER = 3

# HOST = "datatrends.mysql.database.azure.com"
# USERNAME = "admin294@datatrends"
# PASSWORD = "Aa@123456"
# DATABASE = "datatrends"
# ARTICLES_PER_LOAD = 16

# ARTICLES_PER_LOAD = 14*10
# HOST = "eu-cdbr-west-03.cleardb.net"
# USERNAME = "be7e95159ef4b6"
# PASSWORD = "6ae3fcbb"
# DATABASE = "heroku_11541cfc29f14b7"

BASE_URL = "https://vnexpress.net"
PATH_TN = "/tin-nong"
PATH_GT = "/giai-tri-p"
LIST_PATH = ["/thoi-su-p", "/the-gioi-p", "/kinh-doanh/p", "/the-thao/p", "/giai-tri-p", "/phap-luat-p", "/giao-duc-p",
             "/suc-khoe/p","/doi-song/p", "/du-lich/p", "/khoa-hoc-p", "/so-hoa/p", "/oto-xe-may-p"]
BASE_URL_TTO = "https://tuoitre.vn"
PATH_TTO = "/thoi-su.htm"
LIST_PATH_TTO =["/thoi-su.htm","/the-gioi.htm","/kinh-doanh.htm","/the-thao.htm","/giai-tri.htm","/phap-luat.htm","/giao-duc.htm",
               "/giao-duc.htm","/nhip-song-tre.htm","/van-hoa.htm","/khoa-hoc.htm","/gia-that.htm","/xe.htm",]
DAYS = ['Thứ hai, ', 'Thứ ba, ', 'Thứ tư, ', 'Thứ năm, ', 'Thứ sáu, ', 'Thứ bảy, ', 'Chủ nhật, ']

# ---------NEWS---------
def crawNewsDataTTO(url):
    global num
    print("Crawl from ", url)
    response = requests.get(url)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.findAll('li', class_='news-item')
    links = [link.find('a').attrs["href"] for link in titles]
    # print(links)
    data = []
    i=0
    for link in links:
        # if i==1:
        #     break
        # i=i+1
        num = num+1
        # check video
        if link.find("video") != -1:
            continue

        url=BASE_URL_TTO+link
        print("\n",num," ",url)
        news = requests.get(url)
        if news.status_code != 200:
            continue

        soup = BeautifulSoup(news.content, "html.parser")
        soup = html.unescape(soup)
        # check video
        check_video = ""
        check_video = soup.findAll("div", class_="VideoCMS_Caption")
        if check_video != []:
            continue
        # get title
        try:
            title = soup.find("h1", class_="article-title").text
        except:
            continue
        # print("title: ",title)
        # get description
        try:
            description = soup.find("h2", class_="sapo").text
        except:
            continue
        # print("description: ", description)
        # get category
        try:
            category = soup.find("div", class_="bread-crumbs fl")
            category = category.find("a").text
        except:
            category = ""
        # print("category: ", category)
        # get time
        try:
            time2 = soup.find("div", class_="date-time").text
            b = "0123456789: /"
            for char in time2:
                if char not in b:
                    time2 = time2.replace(char, '')
            time2 = time2[0:-2]
            time = time2
            time2 = time2.replace("2020", "20")
            time2 = datetime.strptime(time2, '%d/%m/%y %H:%M')
            wd = date.weekday(time2)
            time = DAYS[wd] + time;
            # print("time2:",time2)
            # print("time:",time)
        except:
            continue
        # get author
        try:
            author = soup.find("div", class_="author").text
            author = author.strip()
        except:
            continue
        listContent = []
        try:
            contents = soup.find("div", class_="content fck").findAll()
        except:
            continue
        for obj in contents:
            obj_info = ""
            obj_type = ""
            if obj.name == "video":
                print("co video")
                break
            if obj.name == "img":
                try:
                    try:
                        data_cke_saved_src = ' '.join(map(str, obj['data-cke-saved-src']))
                    except:
                        data_cke_saved_src = ""
                    if data_cke_saved_src == "":
                        try:
                            obj_info = obj.attrs["src"]
                        except:
                            obj_info = obj.attrs["data-original"]
                        obj_type = "image"
                except:
                    continue

            if obj.name == "p":
                try:
                    try:
                        nameclass = ' '.join(map(str, obj['class']))
                    except:
                        nameclass =""
                    if nameclass == "VCObjectBoxRelatedNewsItemSapo":
                        continue

                    try:
                        dataplaceholder = ' '.join(map(str, obj['data-placeholder']))
                    except:
                        dataplaceholder =""
                    if dataplaceholder == "":
                        obj_type = "text"
                    else:
                        obj_type = "img_des"
                    obj_info = obj.text
                except:
                    continue
            if obj_type != "" and obj_info != "" and obj_info != " " and obj_info != "\n":
                # print(obj_type," ",obj_info)
                obj_info = obj_info.replace("\xa0", " ")
                listContent.append({
                    "info": obj_info.replace("'", "\\'"),
                    "type": obj_type
                })
        data.append({
            "link": url,
            "category": category,
            "title": title,
            "time": time,
            "location": "",
            "description": description,
            "content": listContent,
            "author": author,
            "time2": time2
        })
    return data

def crawlAllTTO():
    # for path in LIST_PATH_TTO:
    #     crawNewsData(BASE_URL_TTO + path)
    saveArticles(BASE_URL_TTO,"")

def saveArticles(base_url, path):
    if base_url==BASE_URL_TTO:
        data = crawNewsDataTTO(base_url + path)
    print("Crawl from ", path)
    if data == []:
        return 1
    number_saved = 0
    is_hot = False
    if path == "/tin-nong":
        is_hot = True
    if base_url+path == "https://tuoitre.vn":
        is_hot =True
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    cursor = db.cursor()
    # delete outdate
    # query = 'delete FROM articles where DATE_SUB(date(now()), INTERVAL {} DAY) > date(created_at)'.format(
    #     DELETE_AFTER)
    # query = "delete FROM articles "
    # query2 = "ALTER TABLE articles AUTO_INCREMENT = 1"
    # try:
    #     cursor.execute(query)
    #     cursor.execute(query2)
    #     db.commit()
    # except:
    #     db.rollback()
    # save to db
    for index, item in enumerate(data[::-1]):
        # if index==1:
        #     break
        _link = item["link"]
        time = item["time"]
        category = item["category"]
        title = item["title"].replace('"', '\\"')
        location = item["location"]
        description = item["description"].replace('"', '\\"')
        author = item["author"].replace('"', '\\"')
        content = item["content"]
        content = str(item["content"]).replace('"', '\\"')
        time2 = item["time2"]
        query = 'INSERT INTO articles(link, time, category, title, location, description, content, author, is_hot,time2, created_at) VALUES ("{}", "{}", "{}", "{}","{}", "{}", "{}", "{}", {}, "{}", {})'.format(
            _link, time, category, title, location, description, content, author, is_hot, time2, 'NOW()')
        try:
            cursor.execute(query)
            # Commit your changes in the database
            db.commit()
            number_saved = number_saved + 1
        except:
            # print(query)
            db.rollback()
            try:
                query = "ALTER TABLE articles AUTO_INCREMENT = {}".format(
                    getLastId())
                cursor.execute(query)
                query = "UPDATE articles set is_hot= {} where link = {} limit 1".format(is_hot, _link)
                cursor.execute(query)
                db.commit()
            except:
                pass
    db.close()
    print("Number news save to db from: ", path, ": ", number_saved)

def getArticlesByCategory(category, offset):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    cursor = db.cursor()
    query = 'SELECT * FROM datatrends.articles where  category LIKE "%{}%" ORDER BY time2 DESC LIMIT {} OFFSET {}'.format(
        category, ARTICLES_PER_LOAD, offset)
    cursor.execute(query)
    dataNews = []
    records = cursor.fetchall()
    for row in records:
        try:
            content = ast.literal_eval(row[7])
        except:
            continue
        dataNews.append({
            "id": row[0],
            "link": row[1],
            "time": row[2],
            "category": row[3],
            "title": row[4],
            "location": row[5],
            "description": row[6],
            "content": content,
            "author": row[8],
            "time2": row[10],
        })
    db.close()
    return dataNews

def getHotNews(offset):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    cursor = db.cursor()
    query = 'SELECT * FROM datatrends.articles where  is_hot = True ORDER BY time2 DESC LIMIT {} OFFSET {}'.format(
        ARTICLES_PER_LOAD, offset)
    cursor.execute(query)
    dataNews = []
    records = cursor.fetchall()
    for row in records:
        try:
            content = ast.literal_eval(row[7])
        except:
            continue
        dataNews.append({
            "id": row[0],
            "link": row[1],
            "time": row[2],
            "category": row[3],
            "title": row[4],
            "location": row[5],
            "description": row[6],
            "content": content,
            "author": row[8],
            "time2": row[10],
        })
    db.close()
    return dataNews

def getNewArticles(offset):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    cursor = db.cursor()
    query = 'SELECT * FROM datatrends.articles ORDER BY time2 DESC LIMIT {} OFFSET {}'.format(
        ARTICLES_PER_LOAD, offset)
    cursor.execute(query)
    dataNews = []
    records = cursor.fetchall()
    for row in records:
        try:
            content = ast.literal_eval(row[7])
        except:
            continue
        dataNews.append({
            "id": row[0],
            "link": row[1],
            "time": row[2],
            "category": row[3],
            "title": row[4],
            "location": row[5],
            "description": row[6],
            "content": content,
            "author": row[8],
            "time2": row[10],
        })
    db.close()
    return dataNews

def getArticleById(id):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    cursor = db.cursor()
    query = "SELECT * FROM articles where id={}".format(id)
    cursor.execute(query)
    dataNews = []
    records = cursor.fetchall()
    for row in records:
        try:
            content = ast.literal_eval(row[7])
        except:
            continue
        dataNews.append({
            "id": row[0],
            "link": row[1],
            "time": row[2],
            "category": row[3],
            "title": row[4],
            "location": row[5],
            "description": row[6],
            "content": content,
            "author": row[8],
            "time2": row[10],
        })
    db.close()
    if dataNews == []:
        return []
    return dataNews[0]

def searchArticles(info, offset):
    db = mysql.connector.connect(user= USERNAME, password= PASSWORD,
                                 host= HOST,
                                 database= DATABASE)
    cursor = db.cursor()
    query = "SELECT * FROM datatrends.articles where (title LIKE '%{}%') or (description LIKE '%{}%')" \
            " ORDER BY time2 DESC LIMIT {} OFFSET {}".format(
                info, info, ARTICLES_PER_LOAD, offset)
    cursor.execute(query)
    dataNews = []
    records = cursor.fetchall()
    for row in records:
        try:
            content = ast.literal_eval(row[7])
        except:
            continue
        dataNews.append({
            "id": row[0],
            "link": row[1],
            "time": row[2],
            "category": row[3],
            "title": row[4],
            "location": row[5],
            "description": row[6],
            "content": content,
            "author": row[8],
            "time2": row[10],
        })
    db.close()
    return dataNews


def getContentById(id):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)

    cursor = db.cursor()
    query = "SELECT content FROM articles where id={}".format(id)
    dataContents = []
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for row in records:
            dataContents = row[0]
            break
    except:
        pass
    db.close()
    try:
        return ast.literal_eval(dataContents)
    except:
        return []


def listToJson(str, data):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y %H%M%S")
    path = "{}{}.json".format(str, dt_string)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def getLastId():
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    query = "SELECT MAX(id) FROM articles"
    result = 0
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for index in records:
            result = index[0]
            break
    except:
        pass
    db.close()
    return result
# number page crawl >=1


def crawlAll(number):
    for index in range(1, number+1)[::-1]:
        for path in LIST_PATH:
            path = path+"{}".format(index)
            saveArticles(BASE_URL, path)
    print("END")

def crawlCategory(path,number):
    for index in range(1, number+1)[::-1]:
            path = path+"{}".format(index)
            saveArticles(BASE_URL, path)

def crawlHotNews():
    saveArticles(BASE_URL, PATH_TN)

# def saveAllToJson():
#     all_data = getNewsFromId(1, getLastId())
#     listToJson("All database ", all_data)


if __name__ == "__main__":
    num =0
    crawlAllTTO()
    # print(crawNewsData(BASE_URL_TTO))
