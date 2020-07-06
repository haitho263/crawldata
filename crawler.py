from bs4 import BeautifulSoup
import requests

def crawNewsData(baseUrl, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    titles = soup.findAll('h3', class_='title-news')
    # print(titles)
    links = [link.find('a').attrs["href"] for link in titles]
    print(links)
    data = []
    for link in links:
        news = requests.get(baseUrl + link)
        soup = BeautifulSoup(news.content, "html.parser")
        try:
            title = soup.find("h1", class_="article-title").text
        except:
            continue
        try:
            abstract = soup.find("h2", class_="sapo").text
        except:
            continue
        body = soup.find("div", id="main-detail-body")
        content = ""
        try:
            content = body.findChildren("p", recursive=False)[0].text + body.findChildren("p", recursive=False)[1].text
        except:
            continue
        # print(body)
        image = body.find("img").attrs["src"]
        data.append({
            "news": news,
            "link": " https://tuoitre.vn/"+link,
            "title": title,
            "abstract": abstract,
            "content": content,
            "image": image,
        })
    return data

def makeFastNews(data):
    # for index, item in enumerate(data):
    #     print("Numer: ", index)
    #     print("Title ", item["title"], "\n")
    #     print("Link ", item["link"], "\n")
    #     print("Abstract ", item["abstract"], "\n")
    #     print("Content ", item["content"], "\n")
    #     print("Image ", item["image"], "\n")s
    print("tho")


if __name__ == "__main__":
    makeFastNews(crawNewsData("https://tuoitre.vn", "https://tuoitre.vn/tin-moi-nhat.htm"))
