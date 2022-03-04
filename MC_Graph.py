from cmath import log10
from app import start
from crawling import Crawling

class Vertex:
    EntirePR0 = 0
    def __init__(self, type, name):
        self.type = type#0: mention, 1:concept
        self.name = name#위키페이지 타이틀명
        self.PR0 = 0
        self.PR = -1
        self.edges = []
    def calcPR0():

        return 
class Edge:
    #global EntireSR
    EntireSR = 0
    def __init__(self, type):
        self.P = -1#전이확률, 가중치 역할
        self.SR = -1#컨셉간의 간선에만 사용
        self.type = type#mention to concept(0) or concept to concept(1)
        #print("type = %d"%(self.type))

    @classmethod
    def conceptToConcept(cls,SR):#컨셉에서 컨셉으로 가는 간선의 생성자 역할
        temp = Edge(1)
        temp.SR = SR
        Edge.EntireSR += SR
        return temp

        
    def calcMtoC(self,mentionBacklinkSet:set,conceptBackinkSet:set):
        a=len(mentionBacklinkSet)
        c=len(mentionBacklinkSet & conceptBackinkSet)
        self.P = c/a

    def calcCtoC(self,set1,set2):#전체 concept 정점에 대한 SR이 필요하다
        
        return

    def printing(self):
        print(self.type)

def calcEntrophy(allBacklinksNum:set, asAnchortextNum:set):#mention A 에 대한 entrophy를 구한다
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
    
def getAnnotation(text, numberOfAnnotation):
    #텍스트는 공백문자만 들어있다고 가정
    #다른 문자가 들어있으면 나중에 따로 파싱함수 만들어야됨
    li = text.split(" ")

    mentionVertex=[]#멘션 노드 저장장소
    mentionSets = set()#비교 연산을 위한 집합

    conceptVertex=[]#컨셉 노드 저장장소

    #각 멘션후보들로 그래프 만들기 시작
    for i in li:
        #멘션이 이미 나온 단어인지 아닌지 확인
        if(len(mentionSets & set([i])) > 0):#같은 단어 있으면 넘긴다
            continue
        concepts = []#concepts에 엔트로피 계산으로 한번 걸러낸 컨셉들을 저장, 안만들면 -1이 출력됨
        if(concepts == -1):#엔트로피가 일정 수치 이상이면 노드 안만듬
            continue

        nowMention = Vertex(0,i)#멘션 노드 하나 만듬
        mentionSets.add(i)
        mentionVertex.append(nowMention)
        for j in concepts:#하나의 멘션에 대한 컨셉들 수만큼 그래프 만듬
            #이미 만든 컨셉 노드중에 같은 노드가 존재하는 지 확인해야함
            index = compareConcepts(conceptVertex,j)
            if(index == -1):#컨셉 노드 없으면 새로만듬
                nowConcept = Vertex(1,j)
                conceptVertex.append(nowConcept)
            else:
                nowConcept = conceptVertex[index]

            edge = Edge(0)#mention to concept 엣지 생성
            edge.calcMtoC(Crawling.getBacklinks(i),Crawling.getBacklinks(j))#P(가중치) 계산
            edge.pointTo = nowConcept#컨셉노드와 엣지 연결
            nowMention.edges.append(edge)#멘션노드와 엣지 연결
        #하나의 멘션에대한 컨셉노드 연결 끝
    #모든 멘션에대한 노드 만들기 끝       
        
    #컨셉노드끼리의 간선 이어야함
    for i in range(0,conceptVertex):#모든 간선을 돌리면 a노드가 b노드를 가리키고 b노드도 a노드를 가리키는 경우 발생, 
        for j in range(0,conceptVertex):#range안에 0을 i로 바꾸면 위에서 말한 이중간선은 없어질듯
            if(i == j):#자기자신을 가리키는 간선 안생김
                continue
            #i 에서 j로 가는 간선만듬
            N = len(conceptVertex)
            SR = calcSR(Crawling.getBacklinks(conceptVertex[i].name),Crawling.getBacklinks(conceptVertex[j].name),N)

            if(SR > 0):#SR값이 0보다커야 간선 추가함
                edge = Edge.conceptToConcept(SR)
                conceptVertex[i].edges.append(edge)
    
    #모든 노드와 간선 생성완료
    #        
    return#출력은 리스트로 할듯
def compareConcepts(conceptVertexList:list, candidateConcept:str):#노드 이미있으면 해당하는 인덱스 출력 없으면 -1
    index = 0
    for i in conceptVertexList:
        if(i.name == candidateConcept):
            return index
        index+=1
    return -1
def calcSR(start_set:set, end_set:set, N):
        
    sameNum = len(start_set & end_set)
        
    #집합 사이즈 저장
    startLen = len(start_set)
    endLen = len(end_set)

    #수식 계산
    SR = 0
    denominator = (log10(N) - log10(min(startLen,endLen)))#분모
    numerator = (log10(max(startLen,endLen)) - log10(sameNum)) #분자
    if(denominator == 0):#분모가 0인 경우가 발생할 수 있음. 임시로 0으로 처리하는걸로 해놓음
        SR = 0
    else:
        SR = 1- numerator / denominator
    
    return SR 


#getAnnotation("testing b c test a",5)
calcSR(set([1,2,3,3,5,7,5,9,7,1,5,4,1]),set([4,2,9,1,12,1,31,23,1,51,8,1,65,15,165,1,1]),10)