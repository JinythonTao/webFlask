# -*- coding: utf-8 -*-
# author: taojin
# time:  2019/9/6 14:33
import time
from datetime import datetime


# time1 = datetime.now()
# print(str(datetime.now()).split(" ")[0])
# print(type(time1))
# time2 = str(datetime.now()).split(".")[0]
# print(time2, type(time2))
# time3 =datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
# print(time3)
# print(type(time3))

def is_weekEnd(timeStmap=None):
    date = time.ctime(timeStmap)[:3]
    day = time.strftime("%Y-%m-%d", time.localtime())
    workingDayList = ["2019-09-29"]
    holiday = ["2019-09-13"]
    if day in workingDayList:
        return False
    elif date == "Sun" or date == "Sat" or day in holiday:
        return True
    else:
        return False


print(is_weekEnd())
