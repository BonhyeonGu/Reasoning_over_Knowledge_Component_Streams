class Util:
    def funcTime(func):
        timeStart = time.time()
        ret = func()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        return ret

    def splitList(lis, splitCount):
        if len(lis) <= splitCount:
            return [lis]

        ret = []
        size = len(lis) // splitCount
        tmp = []
        idx = 0
        for e in lis:
            tmp.append(e)
            idx += 1
            if idx % size == 0:#0
                ret.append(tmp)
                tmp = []
        ret.append(tmp)
        return ret