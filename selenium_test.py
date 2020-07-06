import time
from selenium import webdriver
for index in range(1,100):
    browser = webdriver.Chrome("/Users/leeseok/chromedriver")
    try:
        link="https://chiasenhac.vn/nhac-hot/vietnam.html?playlist={}".format(index)
        browser.get(link)
        browser.find_element_by_id("pills-download-tab").click()
        rs=browser.find_element_by_class_name("download_item")
        print(rs.get_attribute("href"))
        # time.sleep(1)
        browser.quit()
    except:
        browser.quit()
