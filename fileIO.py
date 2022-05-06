import os
import pickle as pic
import numpy as np

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

        self.nameIDToTitle = local + 'ComIDToTitle.npy'
        self.nameTitleToID = local + 'ComTittleToID.pkl'
        self.nameAnkerText = local + 'Arr1.pkl'
        self.nameAnkerTargetID = local + 'Arr2.pkl'
        self.nameNowPageID = local +'Arr3.pkl'
        self.nameBack = local + 'backlinks/'

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
        arr = np.load(self.nameIDToTitle)
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