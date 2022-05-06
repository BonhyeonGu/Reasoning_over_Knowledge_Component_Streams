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

    def unproxy_dict(self, dict_proxy):
        return {k: (dict(v) if isinstance(v, DictProxy) else v)
            for k, v in dict_proxy.items()}