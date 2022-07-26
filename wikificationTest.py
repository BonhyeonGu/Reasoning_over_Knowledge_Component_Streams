from MC_Graph import Graph
import queue
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from concatenWord import concatening
from youtube_transcript_api import YouTubeTranscriptApi

class WikificationTest:
    def __init__(self, gret1, gret2, gret3, gret4, gret5):
        self.gret1 = gret1
        self.gret2 = gret2
        self.gret3 = gret3
        self.gret4 = gret4
        self.gret5 = gret5

    def graphProcess(self, inp):
        return Graph(inp)

    def urlToSplitQueue(self, splitSec, url:str):
        ret = queue.Queue()
        
        tmp = url.split('v=')[1]
        ytid = ''
        for char in tmp:
            if char == '&':
                break
            ytid += char
        
        nowSec = splitSec
        srt:list = YouTubeTranscriptApi.get_transcript(ytid, languages=['en', 'en-US'])
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
        return concatening(out,5)
