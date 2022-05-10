from MC_Graph import Graph
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class WikificationTest:
    def __init__(self, text):
        self.inputForward = text
        self.preProcess()
        g = Graph(self.inputForward)
        result = g.getAnnotation(5)
        print("\n")
        for i in range(len(result)):
            print("node: "+result[i].name)
            print("PR: %lf"%(result[i].PR[g.newIdx]))
            print("")       
        
    def preProcess(self):
        stopWords = set(stopwords.words('english'))
        #stopWords.update(('',''))
        
        tokens = word_tokenize(self.inputForward)
        # convert to lower case
        #tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        
        # remove remaining tokens that are not alphabetic
        words = [word for word in stripped if word.isalpha()]
        
        # filter out stop words
        self.inputForward = [w for w in words if not w in stopWords]
        print(self.inputForward)
        return self.inputForward

with open('./inp.txt', 'rt', encoding='utf-8') as f:
    text = f.read()
WikificationTest(text)