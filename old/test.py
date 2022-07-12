import requests
import time
import datetime

class wikiAPI:
    def __init__(self):
        self.session = requests.Session()
        self.URL = "https://en.wikipedia.org/w/api.php"
    def getlinks(self, p):
        ret = set()
        params = {
            "action": "query",
            "format": "json",
            "titles": p,
            "prop": "links",
            "pllimit": "max"
        }
        response = self.session.get(url=self.URL, params=params)
        data = response.json()
        pages = data["query"]["pages"]
        for key, val in pages.items():
            for link in val["links"]:
                if ':' not in link['title']:
                    ret.add(link["title"])
        while "continue" in data:
            plcontinue = data["continue"]["plcontinue"]
            params["plcontinue"] = plcontinue
            response = self.session.get(url=self.URL, params=params)
            data = response.json()
            pages = data["query"]["pages"]
            for key, val in pages.items():
                for link in val["links"]:
                    if ':' not in link['title']:
                        ret.add(link["title"])
        return ret
    def getBacklinks(self, p):
        ret = set()
        params = {
            "action": "query",
            "format": "json",
            "bltitle": p,
            "list": "backlinks",
            "bllimit": "max"
        }
        response = self.session.get(url=self.URL, params=params)
        data = response.json()
        pages = data["query"]["backlinks"]
        for val in pages:
            if ':' not in val['title']:
                print(val["title"])
                ret.add(val["title"])
        while "continue" in data:
            plcontinue = data["continue"]["blcontinue"]
            params["blcontinue"] = plcontinue
            response = self.session.get(url=self.URL, params=params)
            data = response.json()
            pages = data["query"]["backlinks"]
            for val in pages:
                if ':' not in val['title']:
                    print(val["title"])
                    ret.add(val["title"])
        return ret
w = wikiAPI()
print(w.getBacklinks('dog'))


