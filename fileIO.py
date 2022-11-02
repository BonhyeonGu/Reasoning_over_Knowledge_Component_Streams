import pickle as pic
import numpy as np
from crawling import Crawling

class FileIO():
    def __init__(self, local = './'):
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

        self.arr_idToTitle = np.load(local + 'ComIDToTitle.npy', allow_pickle=True)
        with open(local + 'ComTittleToID.pkl','rb') as f:
            self.dict_titleToID = pic.load(f)
        #-------------------------------------------------------------------
        with open(local + 'anchorData.pkl', 'rb') as f:
            self.dict_full = pic.load(f)

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
    def callDictFull(self):
        return self.dict_full
    #-------------------------------------------------------------------
