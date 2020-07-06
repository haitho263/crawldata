from datetime import datetime
import time
if __name__ == '__main__':
    time2="2/03/20 00:03"
    time2 = datetime.strptime(time2, '%d/%m/%y %H:%M')
    temp="{} {}".format(time2.strftime("%d/%m/%Y"),time2.time())[0:-3]
    print(type())