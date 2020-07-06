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
#
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
LIST_PATH = ["/thoi-su-p", "/the-gioi-p", "/kinh-doanh/p", "/the-thao/p", "/giai-tri-p", "/phap-luat-p", "/giao-duc-p", "/suc-khoe/p",
             "/doi-song/p", "/du-lich/p", "/khoa-hoc-p", "/so-hoa/p", "/oto-xe-may-p"]

BASE_URL_CSN = "https://chiasenhac.vn"
LIST_PATH_CSN =["/nhac-hot/vietnam.html","/nhac-hot/us-uk.html","/nhac-hot/chinese.html","/nhac-hot/korea.html",
       "/nhac-hot/japan.html","/nhac-hot/france.html","/nhac-hot/other.html"]
COUNTRY =["VN","US-UK","CN","KR","JP","FR","OTHER"]

# LIST_PATH_CSN =["/nhac-hot/vietnam.html","/nhac-hot/us-uk.html","/nhac-hot/chinese.html","/nhac-hot/korea.html"]
# COUNTRY =["VN","US-UK","CN","KR"]

BASE_URL_TTO = "https://tuoitre.vn"
LIST_PATH_TTO =["/thoi-su.htm","/the-gioi.htm","/kinh-doanh.htm","/the-thao.htm","/giai-tri.htm","/phap-luat.htm","/giao-duc.htm",
               "/nhip-song-tre.htm","/van-hoa.htm","/khoa-hoc.htm","/gia-that.htm","/xe.htm",]
DAYS = ['Thứ hai, ', 'Thứ ba, ', 'Thứ tư, ', 'Thứ năm, ', 'Thứ sáu, ', 'Thứ bảy, ', 'Chủ nhật, ']

BASE_URL_VTC = "https://vtc.vn"
LIST_PATH_VTC =["","/thoi-su-28.html","/kinh-te-29.html","/the-thao-34.html","/the-gioi-30.html","/giao-duc-31.html",
                "/phap-luat-32.html","/giai-tri-33.html","/suc-khoe-35.html","/gia-dinh-78.html","/khoa-hoc-cong-nghe-82.html"]
LIST_NAME = ["Tin nóng","Thời sự", "Kinh doanh", "Thể thao","Thế giới", "Giáo dục", "Pháp luật", "Giải trí", "Sức khoẻ", "Gia đình","Công nghệ"]
# ---------NEWS---------
def crawlNewsDataVTC(base_url,path,category):
    url=base_url+path
    print("Crawl from ", url)
    response = requests.get(url)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    if url == BASE_URL_VTC:
        titles = soup.findAll('article', class_='top-items')
    else:
        titles = soup.findAll('article', class_='items')
    links = [link.find('a').attrs["href"] for link in titles]
    data = []
    # i = 0
    for link in links:
        # if i==1:
        #     break
        # i=i+1

        if link[0:5]!="https":
            link=BASE_URL_VTC+link
        # Check video
        if link.find("vtc.vn/truyen-hinh-") != -1 or link.find("video") != -1:
            continue
        # print("\n",i," ",link)
        news = requests.get(link)
        if news.status_code != 200:
            continue

        soup = BeautifulSoup(news.content, "html.parser")
        soup = html.unescape(soup)
        # print(soup)
        # check video
        check_video = ""
        check_video = soup.findAll("div", class_="video-element")
        if check_video != []:
            continue

        # get title
        try:
            title = soup.find("header", class_="mb5").text
            title = title.strip()
        except:
            continue
        # print("title: ",title)
        # get description
        try:
            description = soup.find("h4",class_="font16 bold mb15").text
            description = description.strip()
        except:
            continue
        # print("description: ", description)

        # get time
        try:
            time2 = soup.find("span", class_="time-update").text
            time2 = time2[0:-10]
            time = time2
            b = "0123456789: /"
            for char in time2:
                if char not in b:
                    time2 = time2.replace(char, '')
            time2 = time2.replace("2020", "20")
            time2 = time2[2:]
            # time = time2
            time2 = datetime.strptime(time2, '%d/%m/%y %H:%M')
            # print("time:", time)
            # print("time2:", time2)
            # wd = date.weekday(time2)
            # time = DAYS[wd] + time;


        except:
            continue

        # get author
        try:
            author = soup.find("footer", class_="author-make").text
            author = author.replace("\n"," ")
            author = author.strip()
        except:
            continue
        # print(author)
        listContent = []
        try:
            contents = soup.find("div", class_="edittor-content").findAll()
        except:
            continue
        for obj in contents:
            obj_info = ""
            obj_type = ""
            try:
                if obj.name == "img":
                    try:
                        obj_info = obj.attrs["data-src"]
                    except:
                        obj_info = obj.attrs["src"]
                    if obj_info[0:5]!="https":
                        # print(obj_info)
                        continue
                    obj_type = "image"

                if obj.name == "p":
                        try:
                            nameclass = ''.join(map(str, obj['class']))
                        except:
                            nameclass = ""
                        # print(nameclass)
                        if nameclass == "expEdit":
                                obj_type = "img_des"
                        else:
                                obj_type = "text"
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
            "link": link,
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

def crawlAllVTC():
   for index in range(0,11):
       saveArticles(BASE_URL_VTC,LIST_PATH_VTC[index],LIST_NAME[index])

def crawlNewsDataTTO(url):
    # global num
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
        # num = num+1
        # check video
        if link.find("video") != -1:
            continue

        url=BASE_URL_TTO+link
        # print("\n",num," ",url)
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
    for path in LIST_PATH_TTO:
        saveArticles(BASE_URL_TTO, path)
    # saveArticles(BASE_URL_TTO,"/thoi-su.htm")

def crawNewsData(url):
    print("Crawl from ", url)
    response = requests.get(url)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.findAll('h3', class_='title-news')
    if titles == []:
        titles = soup.findAll('h2', class_='title-news')
    links = [link.find('a').attrs["href"] for link in titles]
    data = []
    for link in links:
        # check video
        if link.find("video") != -1:
            continue;
        news = requests.get(link)
        if news.status_code != 200:
            continue

        soup = BeautifulSoup(news.content, "html.parser")
        soup = html.unescape(soup)

        # get title
        try:
            title = soup.find("h1", class_="title-detail").text
        except:
            continue
        # get category
        try:
            category = soup.find("ul", class_="breadcrumb")
            category = category.find("a").text
        except:
            category = ""
        # get time
        try:
            time2 = soup.find("span", class_="date").text
            time = time2[0:-8]
            b = "0123456789: /"
            for char in time2:
                if char not in b:
                    time2 = time2.replace(char, '')
            time2 = time2[2:-2]
            time2 = time2.replace("2020", "20")
            time2 = datetime.strptime(time2, '%d/%m/%y %H:%M')
            # print(time)
        except:

            continue
        # get location
        try:
            location = soup.find("span", class_="location-stamp").text
        except:
            location = ""
        # get description
        try:
            description = soup.find("p", class_="description")
            if location != "":
                description.find(
                    "span", class_="location-stamp").decompose()
                description.find("p", class_="description")

        except:
            continue
        # get listContent
        try:
            contents = soup.find("article", class_="fck_detail").findAll()

            check_video = ""
            check_video = soup.findAll("div", class_="box_embed_video")
            if check_video != []:
                continue

            check_table = ""
            check_table = soup.findAll("table")
            if check_table != []:
                continue

            check_live = ""
            check_live = soup.findAll("article", id="content-live")
            if check_live != []:
                continue

            check_player = ""
            check_player = soup.findAll("div", {"data-oembed-url": True})
            if check_player != []:
                continue

            check_lightgallery = soup.findAll("article", id="lightgallery")
            if check_lightgallery != []:
                continue

            check_lightgallery2 = soup.findAll(
                "div", class_="width-detail-photo")
            if check_lightgallery2 != []:
                continue

            listContent = []

            for obj in contents:
                obj_info = ""
                obj_type = ""
                try:
                    nameclass = ""
                    if obj.name == "p":
                        try:
                            nameclass = ' '.join(map(str, obj['class']))
                        except:
                            nameclass= ""
                        if nameclass == "Image":
                            obj_info = obj.text
                            obj_type = "img_des"
                        else:
                            obj_info = obj.text
                            obj_type = "text"

                    if obj.name == "img":
                        try:
                            obj_info = obj.attrs["data-src"]
                        except:
                            obj_info = obj.attrs["src"]
                        if obj_info[0:5] != "https":
                            continue
                        obj_type = "image"

                    if obj_type != "" and obj_info != ">>Đáp án" and obj_info != " " and obj_info != "\n":
                        obj_info = obj_info.replace("\xa0", " ")
                        listContent.append({
                            "info": obj_info.replace("'", "\\'"),
                            "type": obj_type
                        })
                except:

                    continue
            # get author
            author = ""
            if len(listContent[-1]["info"]) <= 40:
                author = listContent[-1]["info"].replace(
                    "* Tiếp tục cập nhật.", '')
                author = author.replace("\n", "")
                listContent = listContent[0:-1]
        except:
            listContent = ""
            author = ""
        data.append({
            "link": link,
            "category": category,
            "title": title,
            "time": time,
            "location": location,
            "description": description.text,
            "content": listContent,
            "author": author,
            "time2": time2
        })
    return data

def saveArticles(base_url, path,category):

    if base_url==BASE_URL:
        data = crawNewsData(base_url + path)
    else:
        if base_url==BASE_URL_TTO:
            data = crawlNewsDataTTO(base_url + path)
        else:
            if base_url==BASE_URL_VTC:
                data=crawlNewsDataVTC(base_url,path,category)
            else:
                data = []
    print("Crawl from ", base_url+ path)
    if data == []:
        return 1
    number_saved = 0
    is_hot = False
    if path == "/tin-nong" or base_url+path == BASE_URL_TTO or base_url+path == BASE_URL_VTC:
        is_hot = True
    # save json
    # listToJson("one_day ", data)
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
    print("Number news save to db from: ", base_url+path, ": ", number_saved)

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
# --------MUSIC-------

def crawlMusic(url):
    data = []
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.content, "html.parser")
        soup = html.unescape(soup)
        name = soup.find('h2', class_='card-title')
        card_detail = soup.find('div', class_='card card-details')
        image = card_detail.find('img').attrs['src']
        link_mp3 = soup.find('a', class_='download_item').attrs["href"]
        link2 = soup.findAll('a', class_='download_item')
        card_detail = card_detail.findAll('li')
        singer = ""
        composer = ""
        album = ""
        release_year = ""
        for index in card_detail:
            if index.text.find("Ca sĩ:") != -1:
                singer = index.text.replace("Ca sĩ: ","")
            if index.text.find("Sáng tác:") != -1:
                composer = index.text.replace("Sáng tác: ","")
            if index.text.find("Album:") != -1:
                album = index.text.replace("Album: ","")
            if index.text.find("Năm phát hành:") != -1:
                release_year = index.text.replace("Năm phát hành: ","")
        qualities=["128"]
        # print(link_mp3)
        for index in link2:
            temp =''.join(map(str, index['href']))
            if temp.find("/320/") != -1:
                qualities.append("320")
        data.append({
            "name": name.text,
            "link": link_mp3,
            "image": image,
            "singer": singer,
            "composer": composer,
            "album": album,
            "release_year": release_year,
            "link_playlist": url,
            "qualities": qualities,
        })
    except:
        return []
    return data

def createPlayList(path):
    data = []
    for index in range(1,21):
        url=BASE_URL_CSN+path+"?playlist={}".format(index)
        try:
            data.append(crawlMusic(url))
        except:
            continue
    return data

def crawlAndSaveDbMusic():
    deleteDbMusic()
    try:
        db = mysql.connector.connect(user=USERNAME, password=PASSWORD, host=HOST, database=DATABASE)
        cursor = db.cursor()
    except:
        return 0
    number_saved = 0
    for index in range(0,7):
        dataPlayList = createPlayList(LIST_PATH_CSN[index])
        print("crawled playlist: ",LIST_PATH_CSN[index] )
        for data in dataPlayList:
            for index2, obj in enumerate(data):
                name = obj["name"].replace('\"',"\'")
                country = COUNTRY[index]
                link = obj["link"]
                image = obj["image"]
                singer = obj["singer"].replace('\"',"\'")
                composer = obj["composer"].replace('\"',"\'")
                album = obj["album"].replace('\"',"\'")
                release_year = obj["release_year"]
                link_playlist = obj["link_playlist"]
                qualities = obj["qualities"]
                query = "INSERT INTO musics(name, country, link, image, singer, composer, album, release_year, link_playlist, qualities, created_at) VALUES (\"{}\", \"{}\",\"{}\",\"{}\",\"{}\", \"{}\", \"{}\",\"{}\",\"{}\",\"{}\",{})".format(name, country, link, image, singer, composer, album, release_year, link_playlist,qualities,'NOW()')
                try:
                    cursor.execute(query)
                    number_saved = number_saved + 1
                except:
                    continue
    print("saved: ", number_saved)
    db.commit()
    db.close()

def deleteDbMusic():
    try:
        db = mysql.connector.connect(user=USERNAME, password=PASSWORD, host=HOST, database=DATABASE)
        cursor = db.cursor()
    except:
        return 0
    query = "delete FROM musics "
    query2 = "ALTER TABLE musics AUTO_INCREMENT = 1"
    try:
        cursor.execute(query)
        cursor.execute(query2)
        db.commit()
        print("Deleted")
    except:
        db.rollback()

def getMusicByCountry(country):
    try:
        db = mysql.connector.connect(user=USERNAME, password=PASSWORD, host=HOST, database=DATABASE)
        cursor = db.cursor()
    except:
        return 0
    query = "SELECT * FROM musics where country = '{}'".format(country)
    data = []
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        for row in records:
            data.append({
                "id": row[0],
                "name": row[1],
                "country": row[2],
                "link": row[3],
                "image": row[4],
                "singer": row[5],
                "composer": row[6],
                "album": row[7],
                "release_year": row[8],
                "qualities": row[10]
            })
    except:
        return []
    db.close()
    return  data

if __name__ == "__main__":
    # while True:
    #     now = datetime.now()
    #     dt_string = now.strftime("%H %M %S")
    #     ## Crawl New each 1 hour
    #     if now.minute == 0:
    #         crawlHotNews()
    #         crawlAll(1)
    #         crawlAllTTO()
    #         # 23h and 11h (6h and 18h GMT+7)
    #         if now.hour ==23 or now.hour == 11:
    #             crawlAndSaveDbMusic()
    #         time.sleep(60)
    # crawlHotNews()
    # crawlAllTTO()
    # crawlAll(1)
    # crawlAndSaveDbMusic()
    # crawlAndSaveDbMusic()
    crawlAllVTC()