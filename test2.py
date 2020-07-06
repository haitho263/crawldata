import json
from datetime import datetime
import time

def listToJson(str, data):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y %H%M%S")
    path = "{}{}.json".format(str, dt_string)
    with open(path, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    while True:
        now = datetime.now()
        dt_string = now.strftime("%H %M %S")
        if now.minute %5 == 0:
            print("%15 ",dt_string)
            time.sleep(60)








    # data = {}
    # data['people'] = []
    # data['people'].append({
    #     'name': 'Scott',
    #     'website': 'stackabuse.com',
    #     'from': 'Nebraska'
    # })
    # data['people'].append({
    #     'name': 'Larry',
    #     'website': 'google.com',
    #     'from': 'Michigan'
    # })
    # data['people'].append({
    #     'name': 'Tim',
    #     'website': 'apple.com',
    #     'from': 'Alabama'
    # })
    # listToJson("test",data)