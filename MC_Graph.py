#from ast import operator
import operator
import math
import pickle
from threading import Thread, RLock
from multiprocessing import Process, Lock, freeze_support, Manager
from multiprocessing.managers import DictProxy
from typing import Type
from xml.etree.ElementTree import tostring

from util import Util
from crawling import Crawling
from fileIO import FileIO

from random import uniform
import time 
import datetime

class Vertex:
    def __init__(self, type, name):
        self.type = type#0: mention, 1:concept
        self.name = name#위키페이지 타이틀명
        self.PR0 = 0
        self.PR = [1,1]
        self.edges = list()
        self.pointTo = list()
        self.newestPRIdx = 0

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

        
    def calcMtoC(self,entireAnchorNum:int,sameTargetPage:int):
        self.P = sameTargetPage/entireAnchorNum

class Graph:
    def __init__(self, candidateMention:list):#candidateMention: 멘션 후보
        self.mentionList = candidateMention#디버그용
        
        self.craw = Crawling()
        self.LOCK_BACKLINKS = Lock()
        self.LOCK_HAVECOUNT = Lock()
        #---------------------------------------------------
        self.MAXENTROPHY = 1000.0
        #---------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------------------------
 
#-------------------------------------------------------------------------------------------------------------------------------------------------------
    def getDict(self, anchorRange:list):
        entDict = dict()
        for i in range(anchorRange[0], anchorRange[1]):
            try:
                entDict[self.TargetID[i]]+=1
            except KeyError:
                entDict[self.TargetID[i]]=1
        
        return entDict

    def calcEnt(self, entDict:dict, entireNum:int):
        sum=0
        for i in entDict.items():
            sum+=(i[1]/entireNum)*math.log2(i[1]/entireNum)

        return -sum

    def getAnnotation(self, numberOfAnnotation:int):#text는 mention들의 리스트, numberOfAnnotation는 결과 단어 몇개 출력할지 정하는 변수
        self.FileIO = FileIO()
        self.anchorTextRange = self.FileIO.ankerTextToRangeSingle(self.mentionList)
        #없는 텍스트인지 확인해봐야함
        with open('Arr2.pkl', 'rb') as f:
            self.TargetID=pickle.load(f)
        
        li = self.mentionList

        self.mentionVertex=[]#멘션 노드 저장장소
        self.mentionSets = set()#비교 연산을 위한 집합
        self.conceptVertex=[]#컨셉 노드 저장장소

        for i in range(len(li)):
            if(len(self.mentionSets & set(li[i])) > 0):#같은 단어 이미 만들었으면 넘긴다
                continue

            #n = 전체 앵커텍스트 개수
            n = self.anchorTextRange[i][1]-self.anchorTextRange[i][0]

            entDict = self.getDict(self.anchorTextRange[i])
            entrophy = self.calcEnt(entDict,n)

            if entrophy >=self.MAXENTROPHY:
                continue
            
            sortedList = list()
            #+딕셔너리 정렬
            sortedList = sorted(entDict.items(), key = operator.itemgetter(1), reverse=True )
            conceptNum = len(sortedList)

            if conceptNum > 20:
                conceptNum = 20

            nowMention = Vertex(0,li[i])
            
            for j in range(conceptNum):#하나의 멘션에 대한 컨셉들 수만큼 노드, 간선 만듬
                #ni >= 2 인 것만 컨셉노드 생성
                if sortedList[j][1] < 2:
                    break;

                #이미 만든 컨셉 노드중에 같은 노드가 존재하는지 확인
                index = self.compareConcepts(sortedList[j][0])
                if(index == -1):#컨셉 노드 없으면 새로만듬
                    nowConcept = Vertex(1,sortedList[j][0])
                    self.conceptVertex.append(nowConcept)
                else:
                    nowConcept = self.conceptVertex[index]

                edge = Edge(0)#mention to concept 엣지 생성
                edge.calcMtoC(n,sortedList[j][1])#P(가중치) 계산
                #컨셉노드와 엣지 연결
                edge.dest = nowConcept
                edge.start = nowMention

                nowMention.edges.append(edge)#멘션노드와 엣지 연결
                nowConcept.pointTo.append(edge)#컨셉노드에 자신을가리키는 엣지 리스트에 추가
            #하나의 멘션에대한 컨셉노드 연결 끝
        #모든 멘션에대한 노드 만들기 끝 

        #컨셉노드끼리의 간선 이어야함
        for i in range(0,len(self.conceptVertex)):#모든 간선을 돌리면 a노드가 b노드를 가리키고 b노드도 a노드를 가리키는 경우 발생, 
            for j in range(i,len(self.conceptVertex)):#range안에 0을 i로 바꾸면 위에서 말한 이중간선은 없어질듯
                if(i == j):#자기자신을 가리키는 간선 안생김
                    continue
                #i 에서 j로 가는 간선만듬
                N = len(self.conceptVertex)
                SR = self.calcSR(self.FileIO.getBacklinks(self.conceptVertex[j].name),self.FileIO.getBacklinks(self.conceptVertex[j].name),N)

                if(SR > 0):#SR값이 0보다커야 간선 추가함
                    edge = Edge.conceptToConcept(SR)
                    edge.dest = self.conceptVertex[j]
                    edge.start = self.conceptVertex[i]
                    oppositeEdge = Edge.conceptToConcept(SR)
                    oppositeEdge.dest = self.conceptVertex[i]
                    oppositeEdge.start = self.conceptVertex[j]

                    self.conceptVertex[i].edges.append(edge)
                    self.conceptVertex[i].pointTo.append(oppositeEdge)
                    self.conceptVertex[j].edges.append(oppositeEdge)
                    self.conceptVertex[j].pointTo.append(edge)
        
        #모든 노드와 간선 생성완료

        #PR0 계산
        sum = 0
        for i in self.mentionVertex:#z를 제외한 계산 완료
            #u를 앵커텍스트로 가지는 페이지 수 구해서 분자로 넣어주기

            i.PR0 = len(10)/self.craw.getPR0den(i.name)#Crawling에 만들어놓은거 그대로 사용
            sum +=i.PR0
        z = 1/sum
        for i in self.mentionVertex:#z를 곱해줘서 계산 완료
            i.PR0 *= z

        #P(c,c')계산
        for i in self.conceptVertex:
            sum = 0
            for j in i.edges:
                sum += j.SR

            for j in i.edges:
                if sum-j.SR == 0:#컨셉 노드가 적은경우 0인 경우가 발생
                    j.P = 1#임시로 1로 지정하도록 변경
                else:
                    j.P = j.SR/(sum-j.SR)

        #PR계산
        self.calcPR(10)
        supportNodeList = self.calcSupportConcept()
        
        return supportNodeList[:numberOfAnnotation]
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
        if sameNum == 0:#log2에 0이 들어가면 에러뜸
            return 0
        denominator = (math.log2(N) - math.log2(min(startLen,endLen)))
        numerator = (math.log2(max(startLen,endLen)) - math.log2(sameNum)) #분자
        if(denominator == 0):#분모가 0인 경우가 발생할 수 있음. 임시로 0으로 처리하는걸로 해놓음
            SR = 0
        else:
            SR = 1- numerator / denominator
        
        return SR 

    def calcPR(self, repeat:int):
        #repeat:반복계산 횟수
        allVertex = self.mentionVertex + self.conceptVertex
        r =0.1
        for i in range(repeat):
            print("repeat num: %d" %(i+1))
            self.newIdx = i%2
            self.oldIdx = (i+1)%2
            for vertex in allVertex:
                sum=0
                vertex.newestPRIdx = self.newIdx
                for edge in vertex.pointTo:
                    sum += edge.start.PR[self.oldIdx] * edge.P
                vertex.PR[self.newIdx] = r *vertex.PR0  + (1-r)*sum
                print("name: "+ vertex.name + " PR: %lf"%( vertex.PR[self.newIdx]))
        return
    def calcSupportConcept(self):
        #멘션당 PR값이 가장 높은 하나의 노드를 제외하고 나머지 노드를 없앤다
        supportNode = set()
        for mNode in self.mentionVertex:
            maxPR = -1
            maxNode = -1
            for i in range(len(mNode.edges)):
                if maxPR < mNode.edges[i].dest.PR[self.newIdx]:
                    maxPR = mNode.edges[i].dest.PR[self.newIdx]
                    maxNode = i
            #멘션노드가 아무노드와 연결되어있지 않는경우 에러 발생
            temp = mNode.edges[maxNode]
            mNode.edges[maxNode] = mNode.edges[0]
            mNode.edges[0]=temp
            if not(temp.dest in supportNode):
                supportNode.add(temp.dest)
            
            '''
            #나머지 엣지들 제거
            for i in mNode.edges:
                if i == mNode.edges[0]:
                    continue
                i.dest.pointTo.remove(i)
                mNode.edges.remove(i)
            #제거 완료

        #컨셉노드 중 자신을 가리키는 노드가 없는경우 삭제
        for cNode in self.conceptVertex:
            if len(cNode.pointTo) == 0:
                self.conceptVertex.remove(cNode)#이렇게 둘다 삭제해야 하나?
                del cNode
        
            '''
        supportNode = list(supportNode)
        supportNode = sorted(supportNode, key = lambda node: node.PR, reverse=True)
        return supportNode

if __name__ == '__main__':
    freeze_support()
    #ans = Graph(['testing', 'cat', 'rainbow']).getAnnotation(5)
    print("start program")
    timeStart = time.time()
    g = Graph(['cat','dog'])
    result = g.getAnnotation(5)
    print("\n")
    for i in range(len(result)):
        print("node: "+result[i].name)
        print("PR: %lf"%(result[i].PR[g.newIdx]))
        print("")
    timeEnd = time.time()
    sec = timeEnd - timeStart
    result_list = str(datetime.timedelta(seconds=sec))
    print(result_list)