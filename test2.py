import test
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue, freeze_support

import time
import datetime

class WikiInterface(test.wikiAPI):
    def urlToSoup(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    def THREAD_getPageInConceptLink(self, concepts, que):
        ret = []#[concept, set(page,page..), concept, set()]
        for concept in concepts:
            ret.append(concept)
            tmp = set()
            soup = self.urlToSoup("https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/" + concept + "&limit=5000")
            tag = soup.select_one('#mw-whatlinkshere-list')
            if tag != None:
                tags = tag.select("a[href^='/wiki/']")
                for tag in tags:
                    if ':' not in tag['href']:
                        tmp.add(tag['href'].split('/')[2])#/wiki/~
            ret.append(tmp)
        que.put(ret)
        return

    def SUB_getConcepts(self, concepts, que):
        ret = []#[concept, set(page,page..), concept, set()]
        for concept in concepts:
            ret.append(concept)
            
            ret.append(self.getBacklinks(concept))
        que.put(ret)
        return

    def getConcepts(self, mention):
        ret = set()
        pagesInMention = self.getBacklinks(mention)
        concepts = self.getlinks(mention)#컨셉 후보
        #THREAD++++++++++++++++
        sCOUNT=10
        #++++++++++++++++++++++
        #concepts를 여러개로 쪼개기----------------------------------
        i = 0
        conceptsSplit = []
        tmpList = []
        for concept in concepts:
            tmpList.append(concept)
            i += 1
            if i % sCOUNT == 0:
                conceptsSplit.append(tmpList)
                tmpList = []
        conceptsSplit.append(tmpList)
        #----------------------------------------            
        subs = []
        thsPacks = Queue()
        #쓰레드 실행---------------------------------
        for concepts in conceptsSplit:
            th = Process(target=self.SUB_getConcepts, args=(concepts, thsPacks,))
            th.daemon = True
            th.start()
            subs.append(th)
        #----------------------------------------  

        #----------------------------------------  
        x = 0
        while not thsPacks.empty():
            thsPack = thsPacks.get()
            i = 0
            end = len(thsPack) / 2
            while i < end:
                concept = thsPack[i]
                pagesInConcept = thsPack[i + 1]
                x+=1
                if len(pagesInMention & pagesInConcept) >= 2:
                    ret.add(concept)
                i += 2
        return ret

if __name__ == '__main__':
    freeze_support()
    w = WikiInterface()
    timeStart = time.time()
    print(w.getConcepts('dog'))
    timeEnd = time.time()
    sec = timeEnd - timeStart
    result_list = str(datetime.timedelta(seconds=sec))
    print(result_list)
