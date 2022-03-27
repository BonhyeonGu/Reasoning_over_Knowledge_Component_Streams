import os

class FileIO():
    def __init__(self):
        #기회가 되면 알아서 불러오게 해볼까
        #self.okListRequests = ['./Cache/MentionAndRequests/', set()]
        self.okListLinks = ['./Cache/MentionAndgetLinks/', set()]
        self.okListTexts = ['./Cache/MentionAndgetTexts/', set()]
        self.okListBacklinks = ['./Cache/MentionAndgetBackLinks/', set()]
        self.okListEntrophys_Contents = ['./Cache/MentionAndgetEntrophys_getContents/', set()]
        #self.okListContents = ['./Cache/MentionAndgetContents/', set()]

        self.banList = set([':', '<', '>', '|'])
        self.QUESTION = "~Q~"
        self.SLASH = "~S~"
        self.STAR = "~Z~"
        self.DOT = "~D~"

        self.REVERS_SLASH = "~R~"
        self.DOUBLE_DOT = "~P~"
        self.SINGLE_DOT = "~O~"

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
        self.filesToSet(self.okListEntrophys_Contents)
        return

    #cheack&return-----------------------------------------------------------
    #순서대로 리퀘스트(삭제됨), 앵커링크, 앵커텍스트, 백링크, 엔트로피, 콘텐츠이며
    #리퀘스트와 엔트로피는 오직 문자열이기 때문에 다르게 처리한다.
    #리턴이 정수거나 실수이거나 문자열이거나 행렬이다.
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
            #맨 위에는 엔트로피, 나머지는 콘셉트들
            sett = self.okListEntrophys_Contents
        #elif ch == 5:
            #sett = self.okListContents
        if not filename in sett[1]:
            return -1
        else:
            if ch==1 or ch==2 or ch==3:
                ret = set()
            if ch==4:
                ret = []
            f = open(sett[0] + self.nameEncode(filename), 'r', encoding='UTF-8')
            lines = f.read().split('\n')
            f.close()
            size = len(lines) - 1
            if ch==1 or ch==2 or ch==3:
                for i in range(size):
                    ret.add(lines[i])
            if ch==4:
                for i in range(size):
                    ret.append(lines[i])
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
            sett = self.okListEntrophys_Contents
        # elif ch == 5:
        #     sett = self.okListContents
        sett[1].add(filename)
        f = open(sett[0] + realFilename, 'w', encoding='UTF-8')
        for s in inp:
            f.write(s + '\n')
        f.close()
        return
