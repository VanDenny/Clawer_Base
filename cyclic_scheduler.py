import datetime
import pandas as pd
import time


class Cycle_Scheduler:
    def __init__(self):
        pass

    def by_time_point(self, point_list, form_str, func):
        while True:
            while True:
                now = datetime.datetime.now().strftime(form_str)
                print("现在时间是 %s"% now)
                if now in point_list:
                    break
                time.sleep(20)
            print("开始运行 %s" % func.__name__)
            func()

    def datalist(self, beginDate, endDate, freq, form_str):
        date_l = [datetime.strftime(x, form_str) for x in list(pd.date_range(start=beginDate, end=endDate, freq=freq))]
        return date_l

def dosth():
    print('正在做某事！')

if __name__ == '__main__':
    Cycle_Scheduler().by_time_point(['1645', '1650'],'%H%M', dosth)


