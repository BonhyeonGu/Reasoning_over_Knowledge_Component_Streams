#from ast import operator
from base64 import decode
import cProfile
import operator
import math
import pickle

from crawling import Crawling
from fileIO import FileIO

import time 
import datetime
newestPRIdx = 0
newIdx = 0
oldIdx = 1


def getDict(anchorRange:list, TargetID:list):
    entDict = dict()
    for i in range(anchorRange[0], anchorRange[1]):
        try:
            entDict[TargetID[i]]+=1
        except KeyError:
            entDict[TargetID[i]]=1
        
    return entDict

def calcEnt(entDict:dict, entireNum:int):
    sum=0
    for i in entDict.items():
        sum+=(i[1]/entireNum)*math.log2(i[1]/entireNum)

    return -sum

#-----------------------------------------------------------------------------------------------------------------------------------------------------
class Vertex:
    def __init__(self, type, name):
        self.type = type#0: mention, 1:concept
        self.name = name#위키페이지 타이틀명or ID
        self.PR0 = 0
        self.PR = [0.0,0.0]
        self.edges = list()
        self.pointTo = list()

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
        self.MAXENTROPHY = 3.0
        #---------------------------------------------------
        self.craw = Crawling()
        self.FileIO = FileIO()#경로 넣을것!
        #---------------------------------------------------
        
#-------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGlobalIdx(self):
        return newestPRIdx
    def makeAllNode(self):
        #self.FileIO.getTitleToID([])
        print("pickle load")
        timeStart = time.time()
        self.anchorTextRange = self.FileIO.ankerTextToRangeSingle(self.mentionList)
        #없는 텍스트인지 확인해봐야함

        TargetID=list()
        TargetID = self.FileIO.callListAnkerTargetID()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        li = self.mentionList

        self.mentionVertex=[]#멘션 노드 저장장소
        self.conceptVertex=[]#컨셉 노드 저장장소
        mentionVertexAppend = self.mentionVertex.append
        conceptVertexAppend = self.conceptVertex.append

        mentionSets = set()#비교 연산을 위한 집합
        mentionSetAdd = mentionSets.add
        sortedList = list()

        for i in range(len(li)):
            #앵커텍스트로서 존재하지 않는 단어는 제외
            if self.anchorTextRange[i] == -1:
                continue
            if(len(mentionSets & set(li[i])) > 0):#같은 단어 이미 만들었으면 넘긴다
                continue

            #n = 전체 앵커텍스트 개수
            n = self.anchorTextRange[i][1]-self.anchorTextRange[i][0]

            entDict = getDict(self.anchorTextRange[i],TargetID)
            entrophy = calcEnt(entDict,n)

            #엔트로피 통과하는지 확인
            if entrophy >=self.MAXENTROPHY:
                #엔트로피 통과못하면 나중에 제외시키기위해 -1로 변경
                self.anchorTextRange[i] = -1
                continue
            
            #딕셔너리 정렬
            sortedList = sorted(entDict.items(), key = operator.itemgetter(1), reverse=True )
            conceptNum = len(sortedList)

            if conceptNum > 20:
                conceptNum = 20

            #멘션노드 생성
            nowMention = Vertex(0,li[i])
            mentionVertexAppend(nowMention)
            mentionSetAdd(nowMention.name)

            for j in range(conceptNum):#하나의 멘션에 대한 컨셉들 수만큼 노드, 간선 만듬
                #ni >= 2 인 것만 컨셉노드 생성
                if sortedList[j][1] < 2:
                    break;

                #이미 만든 컨셉 노드중에 같은 노드가 존재하는지 확인
                index = self.compareConcepts(sortedList[j][0])
                if(index == -1):#컨셉 노드 없으면 새로만듬
                    nowConcept = Vertex(1,sortedList[j][0])
                    conceptVertexAppend(nowConcept)
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

            sortedList.clear()
            entDict.clear()
        #모든 멘션에대한 노드 만들기 끝 
        del mentionSets
        del TargetID

    def makeEdgeCtoC(self):
        for i in range(0,len(self.conceptVertex)):#모든 간선을 돌리면 a노드가 b노드를 가리키고 b노드도 a노드를 가리키는 경우 발생, 
            for j in range(i,len(self.conceptVertex)):#range안에 0을 i로 바꾸면 위에서 말한 이중간선은 없어질듯
                if(i == j):#자기자신을 가리키는 간선 안생김
                    continue
                #i 에서 j로 가는 간선만듬
                #N = len(self.conceptVertex)
                N=1633324#전체 아이디 개수
                SR = self.calcSR(self.FileIO.getBacklinks(self.conceptVertex[i].name+"_backlinks.pickle"),self.FileIO.getBacklinks(self.conceptVertex[j].name+"_backlinks.pickle"),N)

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

    def calcPR0(self):
        sum = 0
        print("pickle load")
        timeStart = time.time()
        PageID = self.FileIO.callListNowPageID()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        
        delIdx = []
        for i in range(len(self.anchorTextRange)):
            if self.anchorTextRange[i] == -1:
                delIdx.append(i-len(delIdx))
        for i in delIdx:
            self.anchorTextRange.pop(i)

        print("crawling")
        timeStart = time.time()
        for i in range(len(self.anchorTextRange)):#z를 제외한 계산 완료
            #u를 앵커텍스트로 가지는 페이지 수 구해서 분자로 넣어주기

            pageDict = getDict(self.anchorTextRange[i], PageID)
            
            self.mentionVertex[i].PR0 = len(pageDict)/self.craw.getPR0den(self.mentionVertex[i].name)#Crawling에 만들어놓은거 그대로 사용
            sum +=self.mentionVertex[i].PR0
        z = 1/sum
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        for i in self.mentionVertex:#z를 곱해줘서 계산 완료
            i.PR0 *= z

        del PageID

    def calcPosibilityCtoC(self):
        for i in self.conceptVertex:
            sum = 0
            for j in i.edges:
                sum += j.SR

            for j in i.edges:
                if sum-j.SR == 0:#컨셉 노드가 적은경우 0인 경우가 발생
                    j.P = 1#임시로 1로 지정하도록 변경
                else:
                    j.P = j.SR/(sum)

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
            #print("repeat num: %d" %(i+1))
            newIdx = i%2
            oldIdx = (i+1)%2
            for vertex in allVertex:
                sum=0
                newestPRIdx = newIdx
                for edge in vertex.pointTo:
                    sum += edge.start.PR[oldIdx] * edge.P
                vertex.PR[newIdx] = r *vertex.PR0  + (1-r)*sum
                #print("name: "+ vertex.name + " PR: %lf"%( vertex.PR[newIdx]))
            
        allPR = 0.0
        for j in allVertex:
            allPR +=j.PR[newestPRIdx]

        print("allPR: %lf"%(allPR))
        return

    def calcSupportConcept(self):
        #멘션당 PR값이 가장 높은 하나의 노드를 제외하고 나머지 노드를 없앤다
        supportNode = set()
        for mNode in self.mentionVertex:
            maxPR = -1
            maxNode = -1
            for i in range(len(mNode.edges)):
                if maxPR < mNode.edges[i].dest.PR[newIdx]:
                    maxPR = mNode.edges[i].dest.PR[newIdx]
                    maxNode = i
            #멘션노드가 아무노드와 연결되어있지 않는경우 에러 발생

            if maxNode == -1:
                continue
            temp = mNode.edges[maxNode]
            mNode.edges[maxNode] = mNode.edges[0]
            mNode.edges[0]=temp
            if not(temp.dest in supportNode):
                supportNode.add(temp.dest)
            
        supportNode = list(supportNode)
        supportNode = sorted(supportNode, key = lambda node: node.PR, reverse=True)
        return supportNode

    def getAnnotation(self, numberOfAnnotation:int):#text는 mention들의 리스트, numberOfAnnotation는 결과 단어 몇개 출력할지 정하는 변수
        #그래프 노드, 멘션노드에서 컨셉노드로 향하는 엣지 생성
        print("makeAllNode")
        timeStart = time.time()
        self.makeAllNode()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #컨셉노드끼리의 간선 이어야함
        print("makeEdgeCtoC")
        timeStart = time.time()
        self.makeEdgeCtoC()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #PR0 계산
        print("calcPR0")
        timeStart = time.time()
        self.calcPR0()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #P(c,c')계산
        print("calcPosibilityCtoC")
        timeStart = time.time()
        self.calcPosibilityCtoC()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #PR계산
        print("calcPR")
        timeStart = time.time()
        
        self.calcPR(100)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #멘션노드당 하나씩 최고 PR값 높은 컨셉노드 구하기
        print("calcSupportConcept")
        timeStart = time.time()
        supportNodeList = self.calcSupportConcept()
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")

        #ID를 타이틀로 변환시킬 준비
        print("getIDToTitle")
        timeStart = time.time()
        IDList=list()
        for i in supportNodeList[:numberOfAnnotation]:
            IDList.append(int(i.name))
        
        #ID를 타이틀로 변환
        IDList = self.FileIO.getIDToTitle(IDList)
        for i in range(len(IDList)):
            supportNodeList[i].name = IDList[i].decode('utf-8')
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        print(result_list)
        print("")
        return supportNodeList[:numberOfAnnotation]

if __name__ == '__main__':
    print("start program")
    timeStart = time.time()
    #g = Graph(['Pivotal','Moment','Tesla', 'Unveils', 'First', 'Mass-Market','Sedan','Elon_Musk',"Tesla", 'chief', 'executive','cars','employees','owners','electric-car','marker','challenge','demand'])
    g = Graph(['Samba', 'used', 'sysadmin', 'overcome', 'problem', 'interoperability', 'mixed', 'environment', 'Linux', 'Windows', 'It', 'provides', 'common', 'platform', 'Windows', 'Linux', 'common', 'sharing', 'space', 'Domain', 'controller', 'service', 'used', 'centralized', 'administration', 'users', 'groups', 'objects', 'network', 'This', 'service', 'enables', 'us', 'manage', 'authenticate', 'secure', 'users', 'login', 'related', 'data', 'This', 'tutorial', 'explains', 'configure', 'Samba', 'Linux', 'primary', 'domain', 'controller', 'Setup', 'Proper', 'Host', 'Name', 'Make', 'sure', 'setup', 'appropriate', 'hostname', 'static', 'ip', 'If', 'using', 'internal', 'ipaddress', 'like', 'access', 'internet', 'setup', 'appropriate', 'NAT', 'rules', 'firewall', 'In', 'tutorial', 'use', 'tgsexamplecom', 'hostname', 'vi', 'etcsysconfignetwork', 'HOSTNAMEtgsexamplecom', 'Make', 'sure', 'appropriate', 'static', 'ipaddress', 'setup', 'file', 'vi', 'Also', 'assign', 'gateway', 'dns', 'accordingly', 'etcsysconfignetwork', 'etcresolvconf', 'file', 'Verify', 'etchosts', 'file', 'entry', 'similar', 'following', 'vi', 'etchosts', 'tgsexamplecom', 'tgs', 'Also', 'make', 'sure', 'NTP', 'service', 'setup', 'running', 'properly', 'server', 'Install', 'Samba', 'Source', 'On', 'CentOS', 'default', 'samba', 'packages', 'installed', 'minimal', 'installation', 'type', 'First', 'install', 'following', 'dependent', 'packages', 'yum', 'install', 'glibc', 'glibcdevel', 'gcc', 'python', 'libacldevel', 'gitcore', 'openldapdevel', 'Next', 'download', 'samba', 'source', 'shown', 'git', 'clone', 'git', 'gitsambaorgsambagit', 'sambaserver', 'The', 'files', 'downloaded', 'sambaserver', 'directory', 'Install', 'samba', 'server', 'shown', 'cd', 'sambaserver', 'configure', 'enabledebug', 'enableselftest', 'make', 'make', 'install', 'Samba', 'installed', 'default', 'location', 'usrlocalsambabin', 'You', 'see', 'several', 'samba', 'client', 'utilities', 'installed', 'directory', 'cd', 'usrlocalsambabin', 'ls', 'cifsdd', 'ldbsearch', 'ntdbrestore', 'regshell', 'smbcquotas', 'tdbbackup', 'dbwraptool', 'locktest', 'ntdbtool', 'regtree', 'smbget', 'tdbdump', 'eventlogadm', 'masktest', 'ntlmauth', 'rpcclient', 'smbpasswd', 'tdbrestore', 'gentest', 'ndrdump', 'sambatool', 'smbspool', 'tdbtool', 'ldbadd', 'net', 'pdbedit', 'sharesec', 'smbstatus', 'testparm', 'ldbdel', 'nmblookup', 'pidl', 'smbcacls', 'smbtar', 'wbinfo', 'ldbedit', 'profiles', 'smbclient', 'smbtautil', 'ldbmodify', 'ntdbbackup', 'regdiff', 'smbtorture', 'ldbrename', 'ntdbdump', 'regpatch', 'smbcontrol', 'smbtree', 'Setup', 'Domain', 'Provision', 'To', 'start', 'domain', 'provision', 'execute', 'sambatool', 'shown', 'This', 'pickup', 'default', 'hostname', 'domain', 'name', 'configuration', 'files', 'usrlocalsambabinsambatool', 'domain', 'provision', 'Realm', 'EXAMPLECOM', 'Domain', 'EXAMPLE', 'Server', 'Role', 'dc', 'member', 'standalone', 'dc', 'DNS', 'backend', 'SAMBAINTERNAL', 'NONE', 'SAMBAINTERNAL', 'DNS', 'forwarder', 'IP', 'address', 'write', 'none', 'disable', 'forwarding', 'Administrator', 'password', 'Retype', 'password', 'Adding', 'DNS', 'accounts', 'Creating', 'CNMicrosoftDNS', 'CNSystem', 'DCexample', 'DCcom', 'Creating', 'DomainDnsZones', 'ForestDnsZones', 'partitions', 'Populating', 'DomainDnsZones', 'ForestDnsZones', 'partitions', 'Setting', 'samldb', 'rootDSE', 'marking', 'synchronized', 'Fixing', 'provision', 'GUIDs', 'A', 'Kerberos', 'configuration', 'suitable', 'Samba', 'generated', 'Once', 'files', 'installed', 'server', 'ready', 'use', 'Server', 'Role', 'active', 'directory', 'domain', 'controller', 'Hostname', 'tgs', 'NetBIOS', 'Domain', 'EXAMPLE', 'DNS', 'Domain', 'examplecom', 'DOMAIN', 'SID', 'Start', 'Samba', 'Service', 'Start', 'samba', 'service', 'shown', 'usrlocalsambasbinsamba', 'Add', 'following', 'entry', 'rclocal', 'file', 'make', 'sure', 'samba', 'service', 'starts', 'automatically', 'system', 'startup', 'echo', 'usrlocalsambasbinsamba', 'etcrcdrclocal', 'cat', 'etcrcdrclocal', 'touch', 'varlocksubsyslocal', 'usrlocalsambasbinsamba', 'Check', 'Samba', 'Version', 'YOu', 'verify', 'samba', 'version', 'using', 'samba', 'smbclient', 'command', 'shown', 'usrlocalsambasbinsamba', 'V', 'Version', 'usrlocalsambabinsmbclient', 'V', 'Version', 'The', 'following', 'command', 'display', 'Samba', 'shares', 'currently', 'available', 'usrlocalsambabinsmbclient', 'L', 'localhost', 'U', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'Sharename', 'Type', 'Comment', 'netlogon', 'Disk', 'sysvol', 'Disk', 'IPC', 'IPC', 'IPC', 'Service', 'Samba', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'Server', 'Comment', 'Workgroup', 'Master', 'Verify', 'able', 'login', 'using', 'administrator', 'username', 'password', 'usrlocalsambabinsmbclient', 'localhostnetlogon', 'Uadministrator', 'c', 'ls', 'Enter', 'administrator', 'password', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'D', 'Fri', 'Feb', 'D', 'Fri', 'Feb', 'blocks', 'size', 'blocks', 'available', 'Verify', 'Domains', 'Now', 'let', 'us', 'check', 'domain', 'functioning', 'expected', 'Check', 'SRV', 'A', 'record', 'shown', 'host', 'SRV', 'ldaptcpexamplecom', 'ldaptcpexamplecom', 'SRV', 'record', 'tgsexamplecom', 'host', 'SRV', 'kerberosudpexamplecom', 'kerberosudpexamplecom', 'SRV', 'record', 'tgsexamplecom', 'host', 'A', 'tgsexamplecom', 'tgsexamplecom', 'address', 'Use', 'sambatool', 'command', 'verify', 'realm', 'name', 'shown', 'usrlocalsambabinsambatool', 'testparm', 'suppressprompt', 'grep', 'realm', 'realm', 'EXAMPLECOM', 'Configure', 'Kerberos', 'Copy', 'sample', 'file', 'etc', 'directory', 'cp', 'Set', 'defaultrealm', 'domain', 'name', 'In', 'case', 'set', 'examplecom', 'cat', 'libdefaults', 'defaultrealm', 'EXAMPLECOM', 'dnslookuprealm', 'false', 'dnslookupkdc', 'true', 'Use', 'kinit', 'command', 'make', 'sure', 'Kerberos', 'setup', 'properly', 'shown', 'kinit', 'administrator', 'EXAMPLECOM', 'Password', 'administrator', 'EXAMPLECOM', 'Warning', 'Your', 'password', 'expire', 'days', 'Fri', 'Apr', 'Finally', 'use', 'Windows', 'remote', 'administrator', 'tool', 'connect', 'Samba', 'server', 'use', 'domain', 'controller', 'If', 'face', 'issues', 'process', 'make', 'sure', 'bring', 'system', 'uptodate', 'updating', 'packages', 'You', 'also', 'disable', 'SELinux', 'temporarily', 'review', 'auditlog', 'SELinux', 'related', 'error', 'messages', 'Also', 'make', 'sure', 'IPTables', 'rules', 'blocking', 'ports', 'required', 'Samba', 'communicate', 'servers'])
    result=g.getAnnotation(5)
    print("\n")
    for i in range(len(result)):
        print("node: "+result[i].name)
        print("PR: %lf"%(result[i].PR[newestPRIdx]))
    timeEnd = time.time()
    sec = timeEnd - timeStart
    result_list = str(datetime.timedelta(seconds=sec))
    print(result_list)
