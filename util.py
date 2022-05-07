import time 
from multiprocessing.managers import DictProxy, ListProxy

class Util:
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

    def unproxy_dict(dict_proxy):
        return {k: (dict(v) if isinstance(v, DictProxy) else v)
            for k, v in dict_proxy.items()}
    
    def unproxy_list(list_proxy):
        return {(list(v) if isinstance(v, ListProxy) else v)
            for  v in list_proxy}

    def outputConsoleTime():
        now = time.localtime()
        print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
