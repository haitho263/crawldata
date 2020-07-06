from datetime import datetime
from bs4 import BeautifulSoup

import requests
import html
# import json
import mysql.connector
#SQL connection data to connect and save the data in

BASE_URL="https://vnexpress.net"
PATH="/tin-nong"
def crawNewsData(baseUrl, url):
    deleleNews(DELETE_AFTER)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.findAll('h3', class_='title-news')
    links = [link.find('a').attrs["href"] for link in titles]
    data = []
    i=1
    for link in links:
        # check video
        if link.find("video") != -1:
            continue
        news = requests.get(link)
        soup = BeautifulSoup(news.content, "html.parser")
        soup = html.unescape(soup)
        # get title
        try:
            title = soup.find("h1", class_="title-detail").text.replace("'",'')
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
            time = soup.find("span", class_="date").text
            b = "0123456789: /"
            for char in time:
                if char not in b:
                    time = time.replace(char, '')
            time = time[0:-7]
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
                description.find("span", class_="location-stamp").decompose()
                description.find("p", class_="description")
        except:
            continue
        # get listContent
        try:
            contents = soup.find("article", class_="fck_detail").findAll()
            # print(contents)
            check_video = ""
            check = soup.findAll("div", class_="box_embed_video")
            if check != []:
                continue

            check_live = ""
            check_live = soup.findAll("article", id="content-live")
            if check_live != []:
                continue

            check_player = ""
            check_player = soup.findAll("div",{"data-oembed-url": True})
            if check_player != []:
                continue

            check_lightgallery = soup.findAll("article", id="lightgallery")
            if check_lightgallery != []:
                continue


            check_lightgallery2 = soup.findAll("div", class_="width-detail-photo")
            if check_lightgallery2 != []:
                continue
            # Vợ tôi
            listContent = []
            a = 0
            for obj in contents:
                obj_info = ""
                obj_type = ""
                try:
                    nameclass = ""
                    if obj.name == "p":
                        nameclass = ' '.join(map(str, obj['class']))
                        if nameclass == "Image":
                            obj_info = obj.text
                            obj_type = "img_des"
                        else:
                            obj_info = obj.text
                            obj_type = "text"
                    # image = body.find("img").attrs["src"]
                    if obj.name == "img":
                        obj_info = obj.attrs["data-src"]
                        obj_type = "image"
                    if obj_info != "" and obj_type != "":

                        listContent.append({
                            "info": obj_info,
                            "type": obj_type
                        })
                except:
                    continue
            # get author
            author = ""
            if len(listContent[-1]["info"]) <= 40:
                author = listContent[-1]["info"].replace("* Tiếp tục cập nhật.",'')
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
        })
    return data

def saveNews(data):
    number_saved = 0
    # save json
    # listToJson("one_day ",data)
    # Open database connection
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # save db
    for index, item in enumerate(data[::-1]):
        check = 0
        _link = item["link"]
        time = item["time"]
        category = item["category"]
        title = item["title"]
        location = item["location"]
        description = item["description"]
        author = item["author"]
        content = item["content"]
        sql1 = "INSERT INTO articles(link, time, category, title, location, description, author, created_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(_link, time, category, title, location, description, author,'NOW()')
        try:
            # Execute the SQL command - save to articles
            cursor.execute(sql1)
            # Commit your changes in the database
            db.commit()
            number_saved = number_saved + 1
            check = 1
        except:
            check = 0
            sql2 = "ALTER TABLE articles AUTO_INCREMENT = {}".format(getLastId())
            cursor.execute(sql2)
            db.commit()
            # Rollback in case there is any error
            db.rollback()
        if check == 1:
            sql = "SELECT MAX(id) FROM articles"
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Get the result
                result = cursor.fetchone()
                # Set the articles_id
                articles_id = result[0]
                # print(articles_id)
            except:
                # Rollback in case there is any error
                db.rollback()
                # on error set the articles_id to -1
                articles_id = -1
            # save content
            for index2, item2 in enumerate(content):
                info = item2["info"]
                type = item2["type"]
                sql3 = "INSERT INTO contents(articles_id, info, type, created_at) VALUES ('{}', '{}', '{}', {})".format(articles_id, info, type,'NOW()')
                # print(sql2)
                try:
                    # Execute the SQL command - save to articles
                    cursor.execute(sql3)
                    # Commit your changes in the database
                    db.commit()
                except:
                    # Rollback in case there is any error
                    db.rollback()
            content=[]

    db.close()
    # saveAllToJson()
    print("Number news save to db: ",number_saved)

# number day save in db
def deleleNews(number):
    # Open database connection
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    sqlquery="delete FROM articles where DATE_SUB(now(), INTERVAL {} DAY) > created_at".format(number)
    try:
        # Execute the SQL command
        cursor.execute(sqlquery)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    db.close()
# get News by ArticlesID
def getNewsById(start,end):
    # Open database connection
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    sqlquery="SELECT * FROM datatrends.articles where {}<=id && id<={}".format(start,end)
    dataNews=[]
    try:
        # Execute the SQL command
        cursor.execute(sqlquery)
        records = cursor.fetchall()
        for row in records:
            dataNews.append({
                "id": row[0],
                "link": row[1],
                "time": row[2],
                "category": row[3],
                "title": row[4],
                "location":  row[5],
                "description": row[6],
                "content": getContentsByArticlesId(row[0]),
                "author": row[7],
            })
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    db.close()
    return dataNews
# get Contents by ArticlesID
def getContentsByArticlesId(articles_id):
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    sqlquery = "SELECT * FROM datatrends.contents where articles_id={}".format(articles_id)
    dataContents = []
    try:
        # Execute the SQL command
        cursor.execute(sqlquery)
        records = cursor.fetchall()
        for row in records:
            dataContents.append({
                "id": row[0],
                "articles_id": row[1],
                "info": row[2],
                "type": row[3],
            })
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    db.close()
    return dataContents

def listToJson(str,data):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y %H%M%S")
    path="{}{}.json".format(str,dt_string)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def getLastId():
    db = mysql.connector.connect(user=USERNAME, password=PASSWORD,
                                 host=HOST,
                                 database=DATABASE)
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    sqlquery = "SELECT MAX(id) FROM articles"
    result = -1
    try:
        # Execute the SQL command
        cursor.execute(sqlquery)
        records = cursor.fetchall()
        for index in records:
            result = index[0]
            break
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()
    db.close()
    return result

def saveAllToJson():
    all_data = getNewsById(1,getLastId())
    listToJson("All database ",all_data)

if __name__ == "__main__":
    # for index in range(1,200):
    #     link="https://vnexpress.net/thoi-su-p{}".format(index)
    #     saveNews(crawNewsData("https://vnexpress.net",link))
    saveNews(crawNewsData(BASE_URL,BASE_URL + PATH))
    # b=getLastId()
    # aaa=getNewsById(90-15,90)
    # print(aaa)
