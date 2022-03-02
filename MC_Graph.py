from cmath import log10


class Vertex:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self.PR0 = 0
        self.PR = -1
        self.edges = []

class Edge:
    #global EntireSR
    EntireSR = 0
    def __init__(self, type):
        self.P = -1#전이확률, 가중치 역할
        self.SR = -1
        self.type = type#mention to concept(0) or concept to concept(1)
        print("type = %d"%(self.type))

    @classmethod
    def conceptToConcept(cls,start_set:list,end_set:list, N:int):#컨셉에서 컨셉으로 가는 간선의 생성자 역할
        temp = Edge(1)
        temp.calcSR(start_set,end_set,N)
        return temp

        
    def calcMtoC(self,a:int,c:int):
        self.P = c/a

    def calcCtoC(self,set1,set2):#전체 concept 정점에 대한 SR이 필요하다
        
        return
    def calcSR(self,start_set, end_set, N):
        sameNum = 0
        #리스트 순회하면서 같은 글자 찾아내는 부분
        #더 효율적인 방법 있으면 그걸로 바꾸는게 좋을듯
        for i in start_set:
            for j in end_set:
                if(i == j):
                    sameNum +=1
        
        #list 사이즈 저장
        startLen = len(start_set)
        endLen = len(end_set)

        #수식 계산
        denominator = (log10(N) - log10(min(startLen,endLen)))#분모
        numerator = (log10(max(startLen,endLen)) - log10(sameNum)) #분자
        
        self.SR = 1- numerator / denominator#분모가 0인 경우가 발생할 수 있음. 예외처리 어떻게 할지 정해야 할듯
        Edge.EntireSR += self.SR#다른계산을 하기 위해서 전체 SR의 합이 필요함
        print(Edge.EntireSR)
        return

    def printing(self):
        print(self.type)

def calcEntrophy(allBacklinksNum, asAnchortextNum):#mention A 에 대한 entrophy를 구한다
    #allBacklinksNum = A로 인해 발생한 concept후보들 각각의 전체 백링크 수
    #asAnchortextNum = 위의 백링크들 중에서 앵커텍스트가 A인 링크개수

    length = len(allBacklinksNum)#길이는 같은걸로 간주한다
    sum=0
    for i in range(length):
        if(asAnchortextNum[i] == 0 or allBacklinksNum[i] == 0):#둘 중 하나라도 0이면 넘김
            continue
        temp = asAnchortextNum[i]/allBacklinksNum[i]
        sum -= temp * log10(temp)

    return sum
    
li = ['10','5']
li2 = ['101','5']
w=Edge.conceptToConcept(li,li2,20)
w1=Edge(0)
w2=Edge(0)
w3=Edge(0)
