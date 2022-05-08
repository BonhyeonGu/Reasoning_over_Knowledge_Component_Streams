import requests
from bs4 import BeautifulSoup
import time
from random import uniform

class Crawling:
    def __init__(self):
        #나중에는 엥커와 백링크, 엔트로피와 콘셉트로 각각 따로 메모리에 셋을 할까
        self.fc.loadSets()

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

    #PR0를 구하는 공식에서 분모로 사용될 내용, 정수 리턴
    def getPR0den(self, u):
        url = "https://en.wikipedia.org/w/index.php?title=Special:Search&limit=20&offset=0&ns0=1&search=" + u
        soup = self.urlToSoup(url)
        tag = soup.select_one('#mw-search-top-table > div.results-info > strong:nth-child(2)')
        if tag == None:
            return 0
        return int(tag.text.replace(',', ''))

