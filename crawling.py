from tkinter import N
import requests
from bs4 import BeautifulSoup

class Crawling:
    def urlToSoup(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    #집합 리턴
    def getLc(self, concept):
        ret = set()

        url = "https://en.wikipedia.org/w/index.php?title=Special:WhatLinksHere/" + concept + "&limit=50000"
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-whatlinkshere-list')
        if tag == None:
            ret = None
        else:
            tags = tag.select("a[href^='/wiki/']")
            for tag in tags:
                ret.add(tag['href'])
        return ret

    #정수 리턴
    def getPR0den(self, u):
        url = "https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&ns0=1&search=" + u
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-search-top-table > div.results-info > strong:nth-child(2)')
        if tag == None:
            return 0
        return int(tag.text.replace(',', ''))

c = Crawling()
print(c.getLc('sdafdfffsfdfd'))
print(c.getPR0den('asdsdfsdfdfafd'))