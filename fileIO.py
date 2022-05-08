import pickle as pic
import numpy as np
from multiprocessing import Process, freeze_support, Manager

from util import Util

class FileIO():
    def __init__(self, local = './'):
        self.DEBUG = True
        self.SPLIT_PROCESS = 3 # +1

        self.banList = set([':', '<', '>', '|'])
        self.QUESTION = "~Q~"
        self.SLASH = "~S~"
        self.STAR = "~Z~"
        self.DOT = "~D~"
        self.REVERS_SLASH = "~R~"
        self.DOUBLE_DOT = "~P~"
        self.SINGLE_DOT = "~O~"

        self.nameIDToTitle = local + 'ComIDToTitle.npy'
        self.nameTitleToID = local + 'ComTittleToID.pkl'
        self.nameAnkerText = local + 'Arr1.pkl'
        self.nameAnkerTargetID = local + 'Arr2.pkl'
        self.nameNowPageID = local +'Arr3.pkl'
        self.nameBack = local + 'backlinks/'

        self.m = Manager()

    #encode/decode----------------------------------------------------
    def nameEncode(self, s:str):
        s = s.replace('?', self.QUESTION)
        s = s.replace('/', self.SLASH)
        s = s.replace('*', self.STAR)
        s = s.replace('.', self.DOT)

        s = s.replace('\\', self.REVERS_SLASH)
        s = s.replace('\"', self.DOUBLE_DOT)
        s = s.replace('\'', self.SINGLE_DOT)
        return s

    def nameDecode(self, s:str):
        s = s.replace(self.QUESTION, '?')
        s = s.replace(self.SLASH, '/')
        s = s.replace(self.STAR, '*')
        s = s.replace(self.DOT, '.')

        s = s.replace(self.REVERS_SLASH, '\\')
        s = s.replace(self.DOUBLE_DOT, '\"')
        s = s.replace(self.SINGLE_DOT, '\'')
        return s

    #dump
    def getBacklinks(self, title:str):
        fileName = self.nameBack + title
        with open(fileName,'rb') as f:
            ret = pic.load(f)
        return ret

    #!!!
    def getIDToTitle(self, inps:list):
        ret = []
        arr = np.load(self.nameIDToTitle, allow_pickle=True)
        for inp in inps:
            ret.append(arr[inp])
        return ret

    def getTitleToID(self, inps:list):
        ret = []
        with open(self.nameTitleToID,'rb') as f:
            dic = pic.load(f)
        for inp in inps:
            ret.append(dic[inp])
        return ret
    
    #-------------------------------------------------------------------

    def ankerTextToRangeSub(self, inps:list, arr:list, ret:dict):
        for inp in inps:
            s = 0
            e = len(arr)
            while(True):
                m = e / 2
                if inp == ret[inp]:
                    for i in range(m, s - 1, -1):
                        if arr[i] != inp:
                            retS = i
                            break
                    for i in range(m, e):
                        if arr[i] != inp:
                            retE = i
                            break
                    ret[inp] = (retS, retE)
                    break
                elif inps < arr[m]:
                    e = m
                else:
                    s = m
    
    def ankerTextToRange(self, inps:list):
        with open(self.nameAnkerText, 'rb') as f:
            arr = pic.load(f)
        inpss = Util.splitList(inps, self.SPLIT_PROCESS)
        pros = []
        ret = self.m.dict()
        for inps in inpss:
            pro = Process(target = self.ankerTextToRangeSub, args=(inps, arr, ret, ))
            pro.daemon = True
            pro.start()
            pros.append(pro)
        
        del(inpss)
        del(inps)

        for pro in pros:
            pro.join()
        return ret

    def ankerTextToRangeSingle(self, inps:list):
        with open(self.nameAnkerText, 'rb') as f:
            arr = pic.load(f)

        ret = []
        for inp in inps:
            inp = inp.encode('utf-8')
            s = 0
            e = len(arr)
            while(True):
                if s == (e - 1):
                    ret.append(-1)
                    break
                m = s + (e - s) // 2
                if inp == arr[m]:
                    for i in range(m, s - 1, -1):
                        if arr[i] != inp:
                            retS = i
                            break
                    for i in range(m, e):
                        if arr[i] != inp:
                            retE = i
                            break
                    ret.append((retS, retE))
                    break
                elif inp < arr[m]:
                    e = m
                else:
                    s = m
        return ret
    #-------------------------------------------------------------------

    def callListAnkerTargetID(self):
        with open(self.nameAnkerTargetID, 'rb') as f:
            ret = pic.load(f)
        return ret

    def callListNowPageID(self):
        with open(self.nameNowPageID, 'rb') as f:
            ret = pic.load(f)
        return ret
    
    #-------------------------------------------------------------------