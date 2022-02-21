import math
import time
import datetime

class Util:
    def funcTime(self, func):
        timeStart = time.time()
        ret = func()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        return ret
        