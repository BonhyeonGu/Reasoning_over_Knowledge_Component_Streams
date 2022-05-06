import requests
from bs4 import BeautifulSoup
from threading import Thread
from queue import Queue
import time
import datetime
from random import uniform

from util import Util
from fileIO import FileIO

from multiprocessing import Process, freeze_support, Pool
from functools import partial

class Crawling:
    def __init__(self):
        self.fc = FileIO()
        #나중에는 엥커와 백링크, 엔트로피와 콘셉트로 각각 따로 메모리에 셋을 할까
        self.fc.loadSets()

    #원래는 urlToSoup함수에 캐시 저장/불러오기를 만들려고 했으나, 해당 함수는 일반 위키페이지를 포함한 모든 페이지에 사용되기에(ex역링크)
    #올바르지 않았다. 따라서 일반 위키 페이지를 검색하는 함수를 전용으로 만드는게 괜찮겠다.
    def urlToSoupOnlyNormal(self, keyword):
        while(True):
            try:
                req = requests.get('https://en.wikipedia.org/wiki/' + keyword)
                break
            except Exception as e:
                print(datetime.datetime.now())
                print("ERROR(AUTO RETRY), crawling.py, urlToSoupOnlyNormal, requests, LINE:28, INPUT:" + keyword + '\n')
                time.sleep(uniform(0.5, 1.0))                
        soup = BeautifulSoup(req.text, 'lxml')
        # tag = soup.select_one('#mw-content-text')
        # if tag == None:
        #     time.sleep(uniform(4.5, 5.5))
        #     return self.urlToSoupOnlyNormal(keyword)
        #self.fc.setToFile(0, keyword, req.text)
        return soup

    def urlToSoup(self, url):
        try:
            req = requests.get(url)
        except Exception as e:
            time.sleep(uniform(0.5, 1.5))
            try:
                req = requests.get(url)
            except Exception as e:
                time.sleep(uniform(0.5, 1.5))
                try:
                    req = requests.get(url)
                except Exception as e:
                    print("오류!!! urlToSoup 커넥션 실패")

        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    #해당 멘션 페이지의 앵커링크들을 찾는다. !!!존재하지 않는 멘션이라는 것도 여기서 필터링 된다. 존재하지 않는 멘션이면 return -1 <---이거 있어야겠네
    def getLinks(self, mention):
        cheack = self.fc.getCache(1, mention)
        if cheack != -1:
            return cheack
        else:
            soup = self.urlToSoupOnlyNormal(mention)
            #---------------------------------------------------------------
            #존재하지 않는 검색어라는 메세지 발생시 None을 리턴
            tag = soup.select_one('#noarticletext > tbody > tr > td > b')
            if tag is not None:
                return -1
            #---------------------------------------------------------------
            tag = soup.select_one('#mw-content-text')
            #---------------------------------------------------------------
            #다른 기타 오류
            if tag == None:
                return -1
            #---------------------------------------------------------------
            ret_links = set()
            ret_texts = set()
            tags = tag.select("a[href^='/wiki/']")
            for tag in tags:
                #중복되지 않았다면, (명확성 안내 링크 삭제, ?자기이름 링크 삭제?, 파일이 아니면, 세미콜론 들어가는거만 빼주면 될거같다.)
                if (tag['href'] not in ret_links)and(':' not in tag['href']):
                    ret_links.add(tag['href'].split('/wiki/')[1])#/wiki/~
                    ret_texts.add(tag.text)
            self.fc.setToFile(1, mention, ret_links)
            self.fc.setToFile(2, mention, ret_texts)
            return ret_links
   
    #해당 멘션 페이지의 앵커텍스트들을 찾는다.
    def getTexts(self, mention):
        cheack = self.fc.getCache(2, mention)
        if cheack != -1:
            return cheack
        else:
            soup = self.urlToSoupOnlyNormal(mention)
            #---------------------------------------------------------------
            #존재하지 않는 검색어라는 메세지 발생시 None을 리턴
            tag = soup.select_one('#noarticletext > tbody > tr > td > b')
            if tag is not None:
                return -1
            #---------------------------------------------------------------
            tag = soup.select_one('#mw-content-text')
            #---------------------------------------------------------------
            #다른 기타 오류 삭제된 페이지 포함
            if tag == None:
                return -1
            #---------------------------------------------------------------
            ret_links = set()
            ret_texts = set()
            tags = tag.select("a[href^='/wiki/']")
            for tag in tags:
                #중복되지 않았다면, (명확성 안내 링크 삭제, ?자기이름 링크 삭제?, 파일이 아니면, 세미콜론 들어가는거만 빼주면 될거같다.)
                if (tag.text not in ret_texts)and(':' not in tag['href']):
                    ret_links.add(tag['href'].split('/wiki/')[1])#/wiki/~
                    ret_texts.add(tag.text)
            self.fc.setToFile(1, mention, ret_links)
            self.fc.setToFile(2, mention, ret_texts)
            return ret_texts

    #해당 단어로 향하는 하이퍼링크가 있는 페이지를 찾는다.Lc 이것을 위키에서는 백링크라 부르더라
    def getBacklinks(self, p):
        cheack = self.fc.getCache(3, p)
        if cheack != -1:
            return cheack
        else:
            ret = set()
            soup = self.urlToSoup("https://en.wikipedia.org/w/index.php?title=Special%3AWhatLinksHere&limit=5000&target=" + p + "&namespace=0")
            tag = soup.select_one('#mw-whatlinkshere-list')
            if tag != None:
                tags = tag.select("a[href^='/wiki/']")
                for tag in tags:
                    if ':' not in tag['href']:
                        ret.add(tag['href'].split('/wiki/')[1])#/wiki/~
            self.fc.setToFile(3, p, ret)
            return ret

    #PR0를 구하는 공식에서 분모로 사용될 내용, 정수 리턴
    def getPR0den(self, u):
        url = "https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&ns0=1&search=" + u
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-search-top-table > div.results-info > strong:nth-child(2)')
        if tag == None:
            return 0
        return int(tag.text.replace(',', ''))

