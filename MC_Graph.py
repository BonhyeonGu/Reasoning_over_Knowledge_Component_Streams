import math
from app import start
from crawling import Crawling

class Vertex:
    def __init__(self, type, name):
        self.type = type#0: mention, 1:concept
        self.name = name#위키페이지 타이틀명
        self.PR0 = 0
        self.PR = -1
        self.oldPR = 0
        self.edges = []

class Edge:
    def __init__(self, type):
        self.P = -1#전이확률, 가중치 역할
        self.SR = -1#컨셉간의 간선에만 사용
        self.type = type#mention to concept(0) or concept to concept(1)
        #print("type = %d"%(self.type))

    @classmethod
    def conceptToConcept(cls,SR):#컨셉에서 컨셉으로 가는 간선의 생성자 역할
        temp = Edge(1)
        temp.SR = SR
        return temp

        
    def calcMtoC(self,mentionBacklinkSet:set,conceptBackinkSet:set):
        a=len(mentionBacklinkSet)
        c=len(mentionBacklinkSet & conceptBackinkSet)
        self.P = c/a


def calcEntrophy(allBacklinksNum:set, asAnchortextNum:set):#mention A 에 대한 entrophy를 구한다
    #allBacklinksNum = A로 인해 발생한 concept후보들 각각의 전체 백링크 수
    #asAnchortextNum = 위의 백링크들 중에서 앵커텍스트가 A인 링크개수

    length = len(allBacklinksNum)#길이는 같은걸로 간주한다
    sum=0
    for i in range(length):
        if(asAnchortextNum[i] == 0 or allBacklinksNum[i] == 0):#둘 중 하나라도 0이면 넘김
            continue
        temp = asAnchortextNum[i]/allBacklinksNum[i]
        sum -= temp * math.log10(temp)

    return sum

class Graph:
    def __init__(self, candidateMention):#candidateMention: 멘션 후보
        self.mentionList = candidateMention#디버그용
        
    def getAnnotation(self, numberOfAnnotation:int):#text는 mention들의 리스트, numberOfAnnotation는 결과 단어 몇개 출력할지 정하는 변수
        crl = Crawling()

        li = self.mentionList

        self.mentionVertex=[]#멘션 노드 저장장소
        self.mentionSets = set()#비교 연산을 위한 집합
        self.conceptVertex=[]#컨셉 노드 저장장소

        #각 멘션들로 그래프 만들기 시작
        for i in li:
            #멘션이 이미 나온 단어인지 아닌지 확인
            if(len(self.mentionSets & set([i])) > 0):#같은 단어 이미 만들었으면 넘긴다
                continue
            #concepts에 엔트로피 계산으로 한번 걸러낸 컨셉들을 저장, 안만들면 -1이 출력됨
            #-----------------------
            #컨셉 20개만 추려야함
            concepts = crl.getConcepts(i)
            
            concepts = list(concepts)[:20]#디버그용으로 임시로 쪼갬
            #------------------------
            nowMention = Vertex(0,i)#멘션 노드 하나 만듬
            self.mentionSets.add(i)
            self.mentionVertex.append(nowMention)

            for j in concepts:#하나의 멘션에 대한 컨셉들 수만큼 노드, 간선 만듬
                #이미 만든 컨셉 노드중에 같은 노드가 존재하는 지 확인해야함
                index = self.compareConcepts(j)
                if(index == -1):#컨셉 노드 없으면 새로만듬
                    nowConcept = Vertex(1,j)
                    self.conceptVertex.append(nowConcept)
                else:
                    nowConcept = self.conceptVertex[index]

                edge = Edge(0)#mention to concept 엣지 생성
                edge.calcMtoC(crl.getBacklinks(i),crl.getBacklinks(j))#P(가중치) 계산
                edge.pointTo = nowConcept#컨셉노드와 엣지 연결
                nowMention.edges.append(edge)#멘션노드와 엣지 연결
            #하나의 멘션에대한 컨셉노드 연결 끝
        #모든 멘션에대한 노드 만들기 끝       
            
        #컨셉노드끼리의 간선 이어야함
        for i in range(0,len(self.conceptVertex)):#모든 간선을 돌리면 a노드가 b노드를 가리키고 b노드도 a노드를 가리키는 경우 발생, 
            for j in range(0,len(self.conceptVertex)):#range안에 0을 i로 바꾸면 위에서 말한 이중간선은 없어질듯
                if(i == j):#자기자신을 가리키는 간선 안생김
                    continue
                #i 에서 j로 가는 간선만듬
                N = len(self.conceptVertex)
                SR = self.calcSR(crl.getBacklinks(self.conceptVertex[i].name),crl.getBacklinks(self.conceptVertex[j].name),N)

                if(SR > 0):#SR값이 0보다커야 간선 추가함
                    edge = Edge.conceptToConcept(SR)
                    self.conceptVertex[i].edges.append(edge)
        
        #모든 노드와 간선 생성완료

        #PR0 계산
        sum = 0
        for i in self.mentionVertex:#z를 제외한 계산 완료
            i.PR0 = len(crl.getBacklinks(i.name))/crl.getPR0den(i.name)#Crawling에 만들어놓은거 그대로 사용
            sum +=i.PR0
        z = 1/sum/len(self.mentionVertex)
        for i in self.mentionVertex:#z를 곱해줘서 계산 완료
            i.PR0 *= z

        #P(c,c')계산
        for i in self.conceptVertex:
            sum = 0
            for j in i.edges:
                sum += j.SR

            for j in i.edges:
                j.P = j.SR/(sum-j.SR)

        #PR계산

        return#출력은 리스트로 할듯
    def compareConcepts(self, candidateConcept:str):#노드 이미있으면 해당하는 인덱스 출력 없으면 -1
        index = 0
        for i in self.conceptVertex:
            if(i.name == candidateConcept):
                return index
            index+=1
        return -1
    def calcSR(self, start_set:set, end_set:set, N):
            
        sameNum = len(start_set & end_set)
            
        #집합 사이즈 저장
        startLen = len(start_set)
        endLen = len(end_set)

        #수식 계산
        SR = 0
        if sameNum == 0:#log10에 0이 들어가면 에러뜸
            return 0
        denominator = (math.log10(N) - math.log10(min(startLen,endLen)))#분모 -> 이거 왜 복소수?
        numerator = (math.log10(max(startLen,endLen)) - math.log10(sameNum)) #분자
        if(denominator == 0):#분모가 0인 경우가 발생할 수 있음. 임시로 0으로 처리하는걸로 해놓음
            SR = 0
        else:
            SR = 1- numerator / denominator
        
        return SR 

    def calcPR(mentionVertex:list, conceptVertex:list, repeat:int):
        r =0.1
        for i in range(repeat):
            for j in mentionVertex:
                j.PR = r *j.PR0  + (1-r)

        return

ans = Graph(['testing', 'cat', 'rainbow']).getAnnotation(5)