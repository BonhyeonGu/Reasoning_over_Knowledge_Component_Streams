import requests
from bs4 import BeautifulSoup
from threading import Thread
from queue import Queue

from util import Util

from multiprocessing import Process, freeze_support, Pool
from functools import partial
import time
import datetime

class Crawling:
    #입력 : 컨셉, 리턴 : 집합
    def urlToSoup(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    #해당 멘션 페이지의 컨셉들을 찾는다. 존재하지 않는 멘션이라는 것도 여기서 필터링 된다. 존재하지 않는 멘션이면 return None
    def getLinks(self, mention):
        ret = set()
        soup = self.urlToSoup('https://en.wikipedia.org/wiki/' + mention)
        tag = soup.select_one('#noarticletext > tbody > tr > td > b')
        #존재하지 않는 검색어라는 메세지 발생시 None을 리턴
        if tag is not None:
            return None
        tag = soup.select_one('#mw-content-text')
        tags = tag.select("a[href^='/wiki/']")
        for tag in tags:
            #중복되지 않았다면, (명확성 안내 링크 삭제, ?자기이름 링크 삭제?, 파일이 아니면, 세미콜론 들어가는거만 빼주면 될거같다.)
            if (tag['href'] not in ret)and(':' not in tag['href']):
                ret.add(tag['href'].split('/')[2])#/wiki/~
        return ret
   
    #해당 단어로 향하는 하이퍼링크가 있는 페이지를 찾는다.Lc 이것을 위키에서는 백링크라 부르더라
    def getBacklinks(self, p):
        ret = set()
        soup = self.urlToSoup("https://en.wikipedia.org/w/index.php?title=Special%3AWhatLinksHere&limit=5000&target=" + p + "&namespace=0")
        tag = soup.select_one('#mw-whatlinkshere-list')
        if tag != None:
            tags = tag.select("a[href^='/wiki/']")
            for tag in tags:
                if ':' not in tag['href']:
                    ret.add(tag['href'].split('/')[2])#/wiki/~
        return ret

    #해당 단어로 향하는 하이퍼링크가 있는 페이지를 찾는다.Lc
    #생각해봤는데... 큐에 넣는 리스트 그 리스트 첫번째를 컨셉명으로 해야 정상적으로 토스가 가능할듯?
    def sub2(self, pagesInMention, concepts):
        ret = set()
        for concept in concepts:
            pagesInConcept = self.getBacklinks(concept)
            if len(pagesInMention & pagesInConcept) >= 2:
                print(concept)

    #getAnkers와 흡사하지만 추가 조건이 붙는다.
    #컨셉은 해당 조건으로 탈락된다. 컨셉으로 가는 하이퍼링크가 있는 페이지들 중에 맨션으로 가는 링크가 있는 페이지들을 새알린 뒤 2개 미만이면 탈락된다.
    def getConceptsSingle(self, mention):
        ret = set()
        pagesInMention = self.getBacklinks(mention)
        concepts = self.getLinks(mention)#컨셉 후보
        for concept in concepts:
            pagesInConcept = self.getBacklinks(concept)
            if len(pagesInMention & pagesInConcept) >= 2:
                ret.add(concept)
        return ret

    def THREAD_getConcepts(self, concepts, que):
        ret = []
        for concept in concepts:
            ret.append(concept)
            ret.append(self.getBacklinks(concept))
        que.put(ret)
        return

    def getConceptsMultiThread(self, mention):
        ret = set()
        TC = 12
        pagesInMention = self.getBacklinks(mention)
        concepts = list(self.getLinks(mention))#컨셉 후보
        conceptss = Util.splitList(concepts, TC)
        ths = []
        packss = Queue(maxsize=0)

        for concepts in conceptss:
            th = Thread(target=self.THREAD_getConcepts, args=(concepts, packss,))
            th.daemon = True
            th.start()
            ths.append(th)
        for th in ths:
            th.join()
        while not packss.empty():
            packs = packss.get()
            idx = 0
            size = len(packs)
            while idx < size:
                if len(pagesInMention & packs[idx+1]) >= 2:
                    ret.add(packs[idx])
                idx += 2
        return ret

    def getConcepts3(self, mention):
        concepts = self.getLinks(mention)#컨셉 후보
        pagesInMention = self.getBacklinks(mention)
        pool = Pool(processes=2)
        func = partial(self.sub2, pagesInMention)
        ret = pool.map(func, concepts)
        pool.close()
        pool.join()
        return ret

    #PR0를 구하는 공식에서 분모로 사용될 내용, 정수 리턴
    def getPR0den(self, u):
        url = "https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&ns0=1&search=" + u
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-search-top-table > div.results-info > strong:nth-child(2)')
        if tag == None:
            return 0
        return int(tag.text.replace(',', ''))

if __name__ == '__main__':
    c = Crawling()
    timeStart = time.time()
    a=c.getConceptsMultiThread('apple')
    print(a)
    print(len(a))
    timeEnd = time.time()
    sec = timeEnd - timeStart
    result_list = str(datetime.timedelta(seconds=sec))
    print(result_list)