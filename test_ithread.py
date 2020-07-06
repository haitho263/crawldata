import threading
import time
from datetime import datetime
def printSomeThing():
    print(time.time())

def action1(arg1, arg2):
    for index in range(arg1,arg2):
        time.sleep(4)
        print(index)

def action2():
    while True:
        time.sleep(3)
        printSomeThing()


threading.Thread(
    target=action1,
    args = (1, 10)
).start()

threading.Thread(
    target=action2,
).start()