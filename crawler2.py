from newspaper import Article

url = 'https://video.vnexpress.net/tin-tuc/nhip-song/nguoi-tho-dien-che-xe-hut-dinh-o-mien-tay-4121633.html'
article = Article(url)
article.download()
article.parse()
print(article.html)