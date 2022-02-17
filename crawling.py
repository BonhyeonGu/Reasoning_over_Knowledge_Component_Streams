import requests
from bs4 import BeautifulSoup

class Crawling:
    #입력 : 컨셉, 리턴 : 집합
    def urlToSoup(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    #해당 멘션 페이지의 컨셉들을 찾는다. 존재하지 않는 멘션이라는 것도 여기서 필터링 된다. 존재하지 않는 멘션이면 return None
    def getAnkers(self, mention):
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
                ret.add(tag['href'])
        return ret
  
    #getAnkers와 흡사하지만 추가 조건이 붙는다.
    #컨셉은 해당 조건으로 탈락된다. 컨셉으로 가는 하이퍼링크가 있는 페이지들 중에 맨션으로 가는 링크가 있는 페이지들을 새알린 뒤 2개 미만이면 탈락된다.
    def getConcepts(self, mention):
        ret = set()
        noms = self.getAnkers(mention)
        for nom in noms:
            c = 0
            pages = self.getPageInConceptLink(nom)

    #해당 단어로 향하는 하이퍼링크가 있는 페이지를 찾는다.Lc
    def getPageInConceptLink(self, p):
        ret = set()
        url = "https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/" + p + "&limit=50000"
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-whatlinkshere-list')
        if tag != None:
            tags = tag.select("a[href^='/wiki/']")
            for tag in tags:
                if ':' not in tag['href']:
                    ret.add(tag['href'].split('/')[2])#/wiki/~
        return ret

    #PR0를 구하는 공식에서 분모로 사용될 내용, 정수 리턴
    def getPR0den(self, u):
        url = "https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&ns0=1&search=" + u
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-search-top-table > div.results-info > strong:nth-child(2)')
        if tag == None:
            return 0
        return int(tag.text.replace(',', ''))

c = Crawling()
print(c.getPageInConceptLink('cat'))