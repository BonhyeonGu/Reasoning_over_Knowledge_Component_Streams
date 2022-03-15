#cache 디렉토리 안에 보관됨
#페이지가 이미 조사된, 콘셉트가 이미 조사된, 역링크가 이미 조사된... 맨션이 무언인지 남기는 파일
#이하 추가 디렉토리로 각 맨션에 해당하는 페이지, 콘셉트, 역링크가 저장됨
#crawling.py 에서 사용됨

from base64 import decode
import os

class FileIO():
    def __init__(self):
        #기회가 되면 알아서 불러오게 해볼까
        #self.okListRequests = ['./Cache/MentionAndRequests/', set()]
        self.okListLinks = ['./Cache/MentionAndgetLinks/', set()]
        self.okListTexts = ['./Cache/MentionAndgetTexts/', set()]
        self.okListBacklinks = ['./Cache/MentionAndgetBackLinks/', set()]
        self.okListEntrophys = ['./Cache/MentionAndgetEntrophys/', set()]
        self.okListContents = ['./Cache/MentionAndgetContents/', set()]

        self.banList = set(['\\', ':', '"', '<', '>', '|'])
        self.QUESTION = "~Q~"
        self.SLASH = "~S~"
        self.STAR = "~Z~"

    #encode/decode----------------------------------------------------
    def nameEncode(self, s:str):
        s = s.replace('?', self.QUESTION)
        s = s.replace('/', self.SLASH)
        s = s.replace('*', self.STAR)
        return s

    def nameDecode(self, s:str):
        s = s.replace(self.QUESTION, '?')
        s = s.replace(self.SLASH, '/')
        s = s.replace(self.STAR, '*')
        return s
    #load--------------------------------------------------------------
    #sub
    def filesToSet(self, sett):
        filenames = os.listdir(sett[0])
        for filename in filenames:
            filename = filename
            sett[1].add(filename)
        return
    #main
    def loadSets(self):
        #self.filesToSet(self.okListRequests)
        self.filesToSet(self.okListLinks)
        self.filesToSet(self.okListTexts)
        self.filesToSet(self.okListBacklinks)
        self.filesToSet(self.okListEntrophys)
        self.filesToSet(self.okListContents)
        return

    #cheack&return-----------------------------------------------------------
    #아래 두개는 더 겹치는게 없게 코딩할 수 있는데, 그냥 보기 편하게 만듬
    #순서대로 리퀘스트, 앵커링크, 앵커텍스트, 백링크, 콘텐츠이며 리퀘스트만 온리 문자열이기 때문에 다르게 처리한다. 리턴이 정수거나 문자열이거나 행렬이다.
    def getCache(self ,ch, filename):
        # if ch == 0:
        #     if not filename in self.okListRequests[1]:
        #         return -1
        #     else:
        #         f = open(self.okListRequests[0] + self.nameEncode(filename), 'r', encoding='UTF-8')
        #         return f.read()
        if ch == 1:
            sett = self.okListLinks
        elif ch == 2:
            sett = self.okListTexts
        elif ch == 3:
            sett = self.okListBacklinks
        elif ch == 4:
            sett = self.okListEntrophys
        elif ch == 5:
            sett = self.okListContents
        if not filename in sett[1]:
            return -1
        else:
            ret = set()
            f = open(sett[0] + self.nameEncode(filename), 'r', encoding='UTF-8')
            lines = f.read().split('\n')
            size = len(lines) - 1
            for i in range(size):
                ret.add(lines[i])
            return ret
        
    #save&add-----------------------------------------------------------
    def setToFile(self, ch, filename, inp):       
        #밴리스트에 들어간 맨션이면 포기한다.
        for c in filename:
            if c in self.banList:
                return
        realFilename = self.nameEncode(filename)
        #파일길이 확인
        if len(realFilename) > 260:
            return

        # if ch == 0:
        #     self.okListRequests[1].add(filename)
        #     f = open(self.okListRequests[0] + realFilename, 'w', encoding='UTF-8')
        #     f.write(inp)
        #     f.close()
        #     return
        if ch == 1:
            sett = self.okListLinks
        elif ch == 2:
            sett = self.okListTexts
        elif ch == 3:
            sett = self.okListBacklinks
        elif ch == 4:
            sett = self.okListEntrophys
        elif ch == 5:
            sett = self.okListContents
        sett[1].add(filename)
        f = open(sett[0] + realFilename, 'w', encoding='UTF-8')
        for s in inp:
            f.write(s + '\n')
        f.close()
        return
