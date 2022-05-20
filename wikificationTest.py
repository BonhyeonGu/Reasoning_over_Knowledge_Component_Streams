from MC_Graph import Graph
import queue
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from concatenWord import concatening
from youtube_transcript_api import YouTubeTranscriptApi

class WikificationTest:
    def __init__(self, url, splitSec):
        sett:queue.Queue = self.urlToSplitQueue(splitSec, url)
        c = 1

        f = open('./out.txt', 'w', encoding='utf-8')
        while sett.qsize() != 0:
            subInSec = sett.get()
            f.write("%s\n" % (subInSec))
            #print(subInSec)
            g = Graph(self.preProcess(subInSec))
            result = g.getAnnotation(5)
            print("")
            print("%d : %d ~ %d" % (c, (splitSec * c - splitSec) / 60, (splitSec * c) / 60))
            f.write("%d : %d ~ %d\n" % (c, (splitSec * c - splitSec) / 60, (splitSec * c) / 60))
            for i in range(len(result)):
                print("%lf : %s"%(result[i].PR[g.IDX], result[i].name))
                f.write("%lf : %s\n"%(result[i].PR[g.IDX], result[i].name))
                #print("node: "+result[i].name)
                #print("PR: %lf"%(result[i].PR[g.IDX]))
                #print("")       
            c += 1
            f.write("\n")
            print("")
        f.close()

    def urlToSplitQueue(self, splitSec, url:str):
        ret = queue.Queue()

        tmp = url.split('?v=')[1]
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

WikificationTest('https://www.youtube.com/watch?v=egD6qsRapNY', 300.0)