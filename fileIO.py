#cache 디렉토리 안에 보관됨
#페이지가 이미 조사된, 콘셉트가 이미 조사된, 역링크가 이미 조사된... 맨션이 무언인지 남기는 파일
#이하 추가 디렉토리로 각 맨션에 해당하는 페이지, 콘셉트, 역링크가 저장됨
#crawling.py 에서 사용됨

import os

class FileIO():
	def __init__(self):

                self.dictStringOfMentionAndRequests = dict()
                self.dictSetOfMentionAndgetLinks = dict()
                self.dictSetOfMentionAndgetBackLinks = dict()
                self.dictSetOfMentionAndgetContents = dict()

                self.FILEREQUESTS = './cache/MentionAndRequests/'
                self.FILELINKS = './cache/MentionAndgetLinks/'
                self.FILEBACKLINKS = './cache/MentionAndgetBackLinks/'
                self.FILECONTENTS = './cache/MentionAndgetContents/'
        #load--------------------------------------------------------------
        #초기 불러오기 서브 루틴
        def filesToDict(self, locale, dic):
                filenames = os.listdir(locale)
                for filename in filenames:
                        f = open(locale + filename)
                        lines = f.readlines()
                        f.close
                        size = len(lines) - 1
                        res = set()
                        for i in range(size):
                                res.add(lines[i])
                        dic[filename] = res
                return
        #초기 불러오기 메인 루틴, 모든 dict를 채운다.
        def loadDicts(self):
                self.filesToDict(self.FILELINKS, self.dictSetOfMentionAndgetLinks)
                self.filesToDict(self.FILEBACKLINKS, self.dictSetOfMentionAndgetBackLinks)
                self.filesToDict(self.FILECONTENTS, self.dictSetOfMentionAndgetContents)

                filenames = os.listdir(self.FILEREQUESTS)
                for filename in filenames:
                        f = open(self.FILEREQUESTS + filename)
                        self.dictStringOfMentionAndRequests[filename] = f.read()
                        f.close
                return

        #cheack&return-----------------------------------------------------------

        #save&add-----------------------------------------------------------
        def setToFile_putDict(self, ch, inp):

