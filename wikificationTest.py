from MC_Graph import Graph
import queue
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from youtube_transcript_api import YouTubeTranscriptApi

class WikificationTest:
    def __init__(self, url):
        sett:queue.Queue = self.urlToSplitQueue(300.0, url)
        while sett.qsize() != 0:
            subInSec = sett.get()
            #print(subInSec)
            g = Graph(self.preProcess(subInSec))
            result = g.getAnnotation(5)
            print("\n")
            for i in range(len(result)):
                print("node: "+result[i].name)
                print("PR: %lf"%(result[i].PR[g.IDX]))
                print("")       

    def urlToSplitQueue(self, splitSec, url:str):
        ret = queue.Queue()

        tmp = url.split('?v=')[1]
        ytid = ''
        for char in tmp:
            if char == '&':
                break
            ytid += char
        
        nowSec = splitSec
        srt:list = YouTubeTranscriptApi.get_transcript(ytid, languages=['en'])
        sentense = ''
        for st in srt:
            if st['start'] >= nowSec:
                ret.put(sentense)
                sentense = ''
                nowSec += splitSec
                if frontSt['start'] + frontSt['duration'] >= nowSec:
                    sentense += frontSt['text'] + '\n'
            sentense += st['text'] + '\n'
            frontSt = st
        ret.put(sentense)
        return ret
            
    def preProcess(self, inp):
        stopWords = set(stopwords.words('english'))
        #stopWords.update(('',''))
        
        tokens = word_tokenize(inp)
        # convert to lower case
        #tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        
        # remove remaining tokens that are not alphabetic
        words = [word for word in stripped if word.isalpha()]
        
        # filter out stop words
        out = [w for w in words if not w in stopWords]
        #print(out)
        return out

with open('./inp.txt', 'rt', encoding='utf-8') as f:
    text = f.read()
WikificationTest('https://www.youtube.com/watch?v=49g2M0Yv4DU')