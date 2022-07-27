import pickle as pic
import numpy as np
from multiprocessing import Process, freeze_support, Manager

from util import Util
from crawling import Crawling

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
        self.nameBack = local + 'backlinks/'
        self.namePr0den = local + 'pr0dens/'
       
        self.craw = Crawling()
        #self.m = Manager()

        self.arr_idToTitle = np.load(local + 'ComIDToTitle.npy', allow_pickle=True)
        with open(local + 'ComTittleToID.pkl','rb') as f:
            self.dict_titleToID = pic.load(f)
        #-------------------------------------------------------------------
        with open(local + 'Arr1.pkl', 'rb') as f:
            self.list_anchorText = pic.load(f)
        with open(local + 'Arr2.pkl', 'rb') as f:
            self.list_anchorTargetID = pic.load(f)
        with open(local +'Arr3.pkl', 'rb') as f:
            self.list_nowPageID = pic.load(f)
        #-------------------------------------------------------------------

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

    def getPR0den(self, anchorText):
        fileName = self.namePr0den + self.nameEncode(anchorText)
        try:
            with open(fileName, "r") as f:
                return int(f.read())
        except:
            pr0den = self.craw.getPR0den(anchorText)
            with open(fileName, "w") as f:
                f.write(str(pr0den))
            return pr0den

    #!!!
    def getIDToTitle(self, inps:list):
        ret = []
        for inp in inps:
            ret.append(self.arr_idToTitle[inp])
        return ret

    def getTitleToID(self, inps:list):
        ret = []
        for inp in inps:
            ret.append(self.dict_titleToID[inp])
        return ret
    
    #-------------------------------------------------------------------

    def anchorTextToRangeSub(self, inps:list, arr:list, ret:dict):
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
    
    def anchorTextToRange(self, inps:list):
        with open(self.nameAnchorText, 'rb') as f:
            arr = pic.load(f)
        inpss = Util.splitList(inps, self.SPLIT_PROCESS)
        pros = []
        ret = self.m.dict()
        for inps in inpss:
            pro = Process(target = self.anchorTextToRangeSub, args=(inps, arr, ret, ))
            pro.daemon = True
            pro.start()
            pros.append(pro)
        
        del(inpss)
        del(inps)

        for pro in pros:
            pro.join()
        return ret

    #-------------------------------------------------------------------

    def anchorTextToRangeSingle(self, inps:list):
        ret = []
        for inp in inps:
            inp = inp.encode('utf-8')
            s = 0
            e = len(self.list_anchorText)
            while(True):
                m = (s + e) // 2
                #print(arr[m])
                if inp == self.list_anchorText[m]:
                    for i in range(m, s - 2, -1):
                        #print(arr[m])
                        if self.list_anchorText[i] != inp:
                            retS = i+1
                            break
                    for i in range(m, e + 2):
                        #print(arr[m])
                        if self.list_anchorText[i] != inp:
                            retE = i
                            break
                    ret.append((retS, retE))
                    break
                elif s >= e:
                    ret.append(-1)
                    break
                elif inp < self.list_anchorText[m]:
                    e = m-1
                else:
                    s = m+1
        return ret
    #-------------------------------------------------------------------

    def callListAnchorTargetID(self):
        return self.list_anchorTargetID

    def callListNowPageID(self):
        return self.list_nowPageID
    
    #-------------------------------------------------------------------
