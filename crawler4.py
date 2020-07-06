from bs4 import BeautifulSoup
import urllib.request

url = 'https://vnexpress.net'
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')
