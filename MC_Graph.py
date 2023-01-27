#from ast import operator
from operator import itemgetter
from math import log2
from collections import defaultdict

from fileIO import FileIO

import time 
import datetime

def getDict(anchorRange:tuple, TargetID:tuple) -> dict:
    entDict = defaultdict(int)
    for i in range(anchorRange[0], anchorRange[1]):
        entDict[TargetID[i]]+=1
        
    return entDict


def calcEnt(entDict:dict, entireNum:int) -> float:
    sum=0
    for i in entDict.items():
        sum+=(i[1]/entireNum)*log2(i[1]/entireNum)

    return -sum

#-----------------------------------------------------------------------------------------------------------------------------------------------------
class Vertex:
    def __init__(self, type:int, name:str):
        self.type = type#0: mention, 1:concept
        self.name = name#위키페이지 타이틀명or ID
        self.PR0 = 0
        self.PR = [0.0,0.0]
        self.edges = list()
        self.pointTo = list()

class Edge:
    def __init__(self, type:int):
        self.P = -1#전이확률, 가중치 역할
        self.SR = -1#컨셉간의 간선에만 사용
        self.type = type#mention to concept(0) or concept to concept(1)
        #print("type = %d"%(self.type))

    @classmethod
    def conceptToConcept(cls,SR:float):#컨셉에서 컨셉으로 가는 간선의 생성자 역할
        temp = Edge(1)
        temp.SR = SR
        return temp

    def calcMtoC(self,entireAnchorNum:int,sameTargetPage:int):
        self.P = sameTargetPage/entireAnchorNum

class Graph:
    def __init__(self, candidateMention:list, fIO):#candidateMention: 멘션 후보
        self.mentionList = candidateMention
        self.MAXENTROPHY = 3.0
        self.IDX = 0
        #---------------------------------------------------
        self.FileIO = fIO#경로 넣을것!
        #---------------------------------------------------
    def makeAllNode(self, mentionVertex:list, conceptVertex:list, ignoreRepeatedWord:bool):
        anchorData = self.FileIO.callDictFull()
        #없는 텍스트인지 확인해봐야함

        li = self.mentionList
        
        #빠른 불러오기
        mentionVertexAppend = mentionVertex.append
        conceptVertexAppend = conceptVertex.append
        GetPR0Den = self.FileIO.getPR0den
        
        sortedList = list()
        conceptCandidateList = list()
        anchorTextNum = list()
        i = -1
        
        #같은 단어 들어오는지 확인하기위한 변수
        mentionChecker = dict()
        for mention in li:
            i += 1
            #앵커텍스트로서 존재하지 않는 단어는 제외
            try:
                #n = 전체 앵커텍스트 개수
                n = anchorData[mention][1] - anchorData[mention][0]
            except KeyError:
                continue

            #같은 단어 들어오면 무시
            if ignoreRepeatedWord == True:
                try:
                    mentionChecker[mention] += 1
                    continue
                except KeyError:
                    mentionChecker[mention] = 1
            
            #서브딕트
            entDict = anchorData[mention][2]

            #엔트로피 계산된 결과
            entrophy = calcEnt(entDict,n)

            #엔트로피 통과하는지 확인
            if entrophy >=self.MAXENTROPHY:
                continue
            anchorTextNum.append(n)

            #서브딕트 (해당(주) Acnhor Text가 가르키는 ID중 하나의 ID, 해당(주) Anchor Text이면서 해당(서브) ID를 가르키는 Anchor 개수)
            #를 가르키는 Anchor 개수별로 내림정렬한 리스트를 만들어 낸다.
            sortedList = sorted(entDict.items(), key = itemgetter(1), reverse=True)
            #그중에서 가장 큰 20개만 들고온다
            conceptCandidateList.append(tuple(sortedList[:20]))

            #멘션노드 생성
            nowMention = Vertex(0,mention)

            #pageDict = getDict(anchorTextRange[i], PageID) #?

            #PR0 계산
            nowMention.PR0 = anchorData[mention][3]/GetPR0Den(mention)#Crawling에 만들어놓은거 그대로 사용

            mentionVertexAppend(nowMention)

        #모든 멘션을 준비하면..
        conceptDict = dict()

        #모든 멘션에 대한 컨셉트 후보들을 튜플로 저장한다.
        conceptCandidateList = tuple(conceptCandidateList)
        anchorTextNum = tuple(anchorTextNum)
        i = -1
        for mentionNode in mentionVertex:
            i += 1
            j = -1
            
            for conceptCandidate in conceptCandidateList[i]:#하나의 멘션에 대한 컨셉들 수만큼 노드, 간선 만듬
                #conceptCandidate의 0번째는 Anchor text가 mentionNode인 Anchor가 가르키는 Target page id 중에 하나 = 즉 0번째는 해당 멘션의 컨셉트 후보
                #1번째는 Anchor text가 mentionNode인 Anchor중 해당 Target page id를 가르키는 Anchor의 개수 = 즉 1번째는 해당 컨셉트 후보로 향하는 anchor의 개수
                j += 1
                #ni >= 2 인 것만 컨셉노드 생성

                #if conceptCandidate[1] < 2:!!!!!!!!! 틀린거 같은데 !!!!
                #    break
                if conceptCandidate[1] < 2:
                    continue

                #이미 만든 컨셉 노드중에 같은 노드가 존재하는지 확인, 있다면 노드를 만들지 않고 간선만 이으면 되기 때문
                try:
                    nowConcept = conceptDict[conceptCandidate[0]]
                except KeyError:
                    #새로운 컨셉트라면 노드로 만든다.
                    nowConcept = Vertex(1, str(conceptCandidate[0]))
                    conceptDict[conceptCandidate[0]] = nowConcept
                    conceptVertexAppend(nowConcept)

                edge = Edge(0)#mention to concept 엣지 생성
                edge.P = conceptCandidate[1] / anchorTextNum[i] #P(가중치) 계산

                #컨셉노드와 엣지 연결
                edge.dest = nowConcept
                edge.start = mentionNode

                mentionNode.edges.append(edge)#멘션노드와 엣지 연결
                nowConcept.pointTo.append(edge)#컨셉노드에 자신을가리키는 엣지 리스트에 추가
            #하나의 멘션에대한 컨셉노드 연결 끝
            
        #모든 멘션에대한 노드 만들기 끝 

    def makeEdgeCtoC(self, conceptVertex:list) -> None:
        N=1633324#전체 아이디 개수
        GetBackLinks = self.FileIO.getBacklinks
        backlink_list = list()
        
        #backlink집합을 가지는 튜플을 만든다
        for i in conceptVertex:
            backlink_list.append(GetBackLinks(i.name + "_backlinks.pickle"))
        backlink_tuple = tuple(backlink_list)

        i = -1
        for startVertex in conceptVertex:
            i+=1
            j=-1
            for endVertex in conceptVertex:
                j+=1
                if(i == j):#자기자신을 가리키는 간선 안생김
                    continue
                #i에서 j로
                
                SR = self.calcSR(backlink_tuple[i],backlink_tuple[j],N)

                if(SR > 0):#SR값이 0보다커야 간선 추가함
                    edge = Edge.conceptToConcept(SR)
                    edge.dest = endVertex
                    edge.start = startVertex
                    # oppositeEdge = Edge.conceptToConcept(SR)
                    # oppositeEdge.dest = conceptVertex[i]
                    # oppositeEdge.start = conceptVertex[j]

                    startVertex.edges.append(edge)
                    # conceptVertex[i].pointTo.append(oppositeEdge)
                    # conceptVertex[j].edges.append(oppositeEdge)
                    endVertex.pointTo.append(edge)

    def calcPR0(self, mentionVertex:list):
        sum = 0
        
        for i in mentionVertex:#z를 제외한 계산 완료
            sum +=i.PR0
        z = 1/sum

        for i in mentionVertex:#z를 곱해줘서 계산 완료
            i.PR0 *= z


    def calcPosibilityCtoC(self, conceptVertex:list):
        for i in conceptVertex:
            sum = 0
            for j in i.edges:
                sum += j.SR

            for j in i.edges:
                if sum-j.SR == 0:#컨셉 노드가 적은경우 0인 경우가 발생
                    j.P = 1#임시로 1로 지정하도록 변경
                else:
                    j.P = j.SR/(sum)

    def calcSR(self, start_set:set, end_set:set, N:int) -> float:
            
        sameNum = len(start_set & end_set)
            
        #집합 사이즈 저장
        startLen = len(start_set)
        endLen = len(end_set)

        #수식 계산
        SR = 0
        if sameNum == 0:#log2에 0이 들어가면 에러뜸
            return 0
        denominator = (log2(N) - log2(min(startLen,endLen)))
        numerator = (log2(max(startLen,endLen)) - log2(sameNum)) #분자
        #분모가 0인 경우가 발생할 수 있음. 임시로 0으로 처리하는걸로 해놓음
        if denominator == 0:
            SR = 0
        else:
            SR = 1- numerator / denominator
        
        return SR 

    def calcPR(self, repeat:int, mentionVertex:list, conceptVertex:list):
        #repeat:반복계산 횟수
        allVertex = mentionVertex + conceptVertex
        r =0.1
        for i in range(repeat):
            #print("repeat num: %d" %(i+1))
            newIdx = i%2
            oldIdx = (i+1)%2
            for vertex in allVertex:
                sum=0
                
                for edge in vertex.pointTo:
                    sum += edge.start.PR[oldIdx] * edge.P
                vertex.PR[newIdx] = r *vertex.PR0  + (1-r)*sum
                #print("name: "+ vertex.name + " PR: %lf"%( vertex.PR[newIdx]))
            
        self.IDX = newIdx
        # allPR = 0.0
        # for j in allVertex:
        #     allPR +=j.PR[self.IDX]

        # print("allPR: %lf"%(allPR))
        return

    def calcSupportConcept(self, mentionVertex:list):
        #멘션당 PR값이 가장 높은 하나의 노드를 제외하고 나머지 노드를 없앤다
        supportNode = set()
        for mNode in mentionVertex:
            maxPR = -1
            maxNode = -1
            for i in range(len(mNode.edges)):
                if maxPR < mNode.edges[i].dest.PR[self.IDX]:
                    maxPR = mNode.edges[i].dest.PR[self.IDX]
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

    def getAnnotation(self, numberOfAnnotation:int, ignoreRepeatedWord:bool = False, debug:bool = False):#text는 mention들의 리스트, numberOfAnnotation는 결과 단어 몇개 출력할지 정하는 변수
        #그래프 노드, 멘션노드에서 컨셉노드로 향하는 엣지 생성
        if debug:
            print("makeAllNode")
        timeStart = time.time()
        mentionVertex=[]#멘션 노드 저장장소
        conceptVertex=[]#컨셉 노드 저장장소
        self.makeAllNode(mentionVertex, conceptVertex, ignoreRepeatedWord)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)
        
        #컨셉노드끼리의 간선 이어야함
        if debug:
            print("makeEdgeCtoC")
        timeStart = time.time()
        self.makeEdgeCtoC(conceptVertex)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)
        #vg.visualize(mentionVertex,conceptVertex)
        #PR0 계산
        if debug:
            print("calcPR0")
        timeStart = time.time()
        self.calcPR0(mentionVertex)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)

        #P(c,c')계산
        if debug:
            print("calcPosibilityCtoC")
        timeStart = time.time()
        self.calcPosibilityCtoC(conceptVertex)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)

        #PR계산
        if debug:
            print("calcPR")
        timeStart = time.time()
        
        self.calcPR(100,mentionVertex,conceptVertex)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)

        #멘션노드당 하나씩 최고 PR값 높은 컨셉노드 구하기
        if debug:
            print("calcSupportConcept")
        timeStart = time.time()
        supportNodeList = self.calcSupportConcept(mentionVertex)
        timeEnd = time.time()
        sec = timeEnd - timeStart
        result_list = str(datetime.timedelta(seconds=sec))
        if debug:
            print(result_list)

        #ID를 타이틀로 변환시킬 준비
        if debug:
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
        if debug:
            print(result_list)
        del IDList
        return supportNodeList[:numberOfAnnotation]

if __name__ == '__main__':       
    print("start program")
    timeStart = time.time()
    g = Graph(['cat', 'dog'], FileIO(local = './'))
    #g = Graph(['Samba', 'used', 'sysadmin', 'overcome', 'problem', 'interoperability', 'mixed', 'environment', 'Linux', 'Windows', 'It', 'provides', 'common', 'platform', 'Windows', 'Linux', 'common', 'sharing', 'space', 'Domain', 'controller', 'service', 'used', 'centralized', 'administration', 'users', 'groups', 'objects', 'network', 'This', 'service', 'enables', 'us', 'manage', 'authenticate', 'secure', 'users', 'login', 'related', 'data', 'This', 'tutorial', 'explains', 'configure', 'Samba', 'Linux', 'primary', 'domain', 'controller', 'Setup', 'Proper', 'Host', 'Name', 'Make', 'sure', 'setup', 'appropriate', 'hostname', 'static', 'ip', 'If', 'using', 'internal', 'ipaddress', 'like', 'access', 'internet', 'setup', 'appropriate', 'NAT', 'rules', 'firewall', 'In', 'tutorial', 'use', 'tgsexamplecom', 'hostname', 'vi', 'etcsysconfignetwork', 'HOSTNAMEtgsexamplecom', 'Make', 'sure', 'appropriate', 'static', 'ipaddress', 'setup', 'file', 'vi', 'Also', 'assign', 'gateway', 'dns', 'accordingly', 'etcsysconfignetwork', 'etcresolvconf', 'file', 'Verify', 'etchosts', 'file', 'entry', 'similar', 'following', 'vi', 'etchosts', 'tgsexamplecom', 'tgs', 'Also', 'make', 'sure', 'NTP', 'service', 'setup', 'running', 'properly', 'server', 'Install', 'Samba', 'Source', 'On', 'CentOS', 'default', 'samba', 'packages', 'installed', 'minimal', 'installation', 'type', 'First', 'install', 'following', 'dependent', 'packages', 'yum', 'install', 'glibc', 'glibcdevel', 'gcc', 'python', 'libacldevel', 'gitcore', 'openldapdevel', 'Next', 'download', 'samba', 'source', 'shown', 'git', 'clone', 'git', 'gitsambaorgsambagit', 'sambaserver', 'The', 'files', 'downloaded', 'sambaserver', 'directory', 'Install', 'samba', 'server', 'shown', 'cd', 'sambaserver', 'configure', 'enabledebug', 'enableselftest', 'make', 'make', 'install', 'Samba', 'installed', 'default', 'location', 'usrlocalsambabin', 'You', 'see', 'several', 'samba', 'client', 'utilities', 'installed', 'directory', 'cd', 'usrlocalsambabin', 'ls', 'cifsdd', 'ldbsearch', 'ntdbrestore', 'regshell', 'smbcquotas', 'tdbbackup', 'dbwraptool', 'locktest', 'ntdbtool', 'regtree', 'smbget', 'tdbdump', 'eventlogadm', 'masktest', 'ntlmauth', 'rpcclient', 'smbpasswd', 'tdbrestore', 'gentest', 'ndrdump', 'sambatool', 'smbspool', 'tdbtool', 'ldbadd', 'net', 'pdbedit', 'sharesec', 'smbstatus', 'testparm', 'ldbdel', 'nmblookup', 'pidl', 'smbcacls', 'smbtar', 'wbinfo', 'ldbedit', 'profiles', 'smbclient', 'smbtautil', 'ldbmodify', 'ntdbbackup', 'regdiff', 'smbtorture', 'ldbrename', 'ntdbdump', 'regpatch', 'smbcontrol', 'smbtree', 'Setup', 'Domain', 'Provision', 'To', 'start', 'domain', 'provision', 'execute', 'sambatool', 'shown', 'This', 'pickup', 'default', 'hostname', 'domain', 'name', 'configuration', 'files', 'usrlocalsambabinsambatool', 'domain', 'provision', 'Realm', 'EXAMPLECOM', 'Domain', 'EXAMPLE', 'Server', 'Role', 'dc', 'member', 'standalone', 'dc', 'DNS', 'backend', 'SAMBAINTERNAL', 'NONE', 'SAMBAINTERNAL', 'DNS', 'forwarder', 'IP', 'address', 'write', 'none', 'disable', 'forwarding', 'Administrator', 'password', 'Retype', 'password', 'Adding', 'DNS', 'accounts', 'Creating', 'CNMicrosoftDNS', 'CNSystem', 'DCexample', 'DCcom', 'Creating', 'DomainDnsZones', 'ForestDnsZones', 'partitions', 'Populating', 'DomainDnsZones', 'ForestDnsZones', 'partitions', 'Setting', 'samldb', 'rootDSE', 'marking', 'synchronized', 'Fixing', 'provision', 'GUIDs', 'A', 'Kerberos', 'configuration', 'suitable', 'Samba', 'generated', 'Once', 'files', 'installed', 'server', 'ready', 'use', 'Server', 'Role', 'active', 'directory', 'domain', 'controller', 'Hostname', 'tgs', 'NetBIOS', 'Domain', 'EXAMPLE', 'DNS', 'Domain', 'examplecom', 'DOMAIN', 'SID', 'Start', 'Samba', 'Service', 'Start', 'samba', 'service', 'shown', 'usrlocalsambasbinsamba', 'Add', 'following', 'entry', 'rclocal', 'file', 'make', 'sure', 'samba', 'service', 'starts', 'automatically', 'system', 'startup', 'echo', 'usrlocalsambasbinsamba', 'etcrcdrclocal', 'cat', 'etcrcdrclocal', 'touch', 'varlocksubsyslocal', 'usrlocalsambasbinsamba', 'Check', 'Samba', 'Version', 'YOu', 'verify', 'samba', 'version', 'using', 'samba', 'smbclient', 'command', 'shown', 'usrlocalsambasbinsamba', 'V', 'Version', 'usrlocalsambabinsmbclient', 'V', 'Version', 'The', 'following', 'command', 'display', 'Samba', 'shares', 'currently', 'available', 'usrlocalsambabinsmbclient', 'L', 'localhost', 'U', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'Sharename', 'Type', 'Comment', 'netlogon', 'Disk', 'sysvol', 'Disk', 'IPC', 'IPC', 'IPC', 'Service', 'Samba', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'Server', 'Comment', 'Workgroup', 'Master', 'Verify', 'able', 'login', 'using', 'administrator', 'username', 'password', 'usrlocalsambabinsmbclient', 'localhostnetlogon', 'Uadministrator', 'c', 'ls', 'Enter', 'administrator', 'password', 'Domain', 'EXAMPLE', 'OS', 'Windows', 'Server', 'Samba', 'D', 'Fri', 'Feb', 'D', 'Fri', 'Feb', 'blocks', 'size', 'blocks', 'available', 'Verify', 'Domains', 'Now', 'let', 'us', 'check', 'domain', 'functioning', 'expected', 'Check', 'SRV', 'A', 'record', 'shown', 'host', 'SRV', 'ldaptcpexamplecom', 'ldaptcpexamplecom', 'SRV', 'record', 'tgsexamplecom', 'host', 'SRV', 'kerberosudpexamplecom', 'kerberosudpexamplecom', 'SRV', 'record', 'tgsexamplecom', 'host', 'A', 'tgsexamplecom', 'tgsexamplecom', 'address', 'Use', 'sambatool', 'command', 'verify', 'realm', 'name', 'shown', 'usrlocalsambabinsambatool', 'testparm', 'suppressprompt', 'grep', 'realm', 'realm', 'EXAMPLECOM', 'Configure', 'Kerberos', 'Copy', 'sample', 'file', 'etc', 'directory', 'cp', 'Set', 'defaultrealm', 'domain', 'name', 'In', 'case', 'set', 'examplecom', 'cat', 'libdefaults', 'defaultrealm', 'EXAMPLECOM', 'dnslookuprealm', 'false', 'dnslookupkdc', 'true', 'Use', 'kinit', 'command', 'make', 'sure', 'Kerberos', 'setup', 'properly', 'shown', 'kinit', 'administrator', 'EXAMPLECOM', 'Password', 'administrator', 'EXAMPLECOM', 'Warning', 'Your', 'password', 'expire', 'days', 'Fri', 'Apr', 'Finally', 'use', 'Windows', 'remote', 'administrator', 'tool', 'connect', 'Samba', 'server', 'use', 'domain', 'controller', 'If', 'face', 'issues', 'process', 'make', 'sure', 'bring', 'system', 'uptodate', 'updating', 'packages', 'You', 'also', 'disable', 'SELinux', 'temporarily', 'review', 'auditlog', 'SELinux', 'related', 'error', 'messages', 'Also', 'make', 'sure', 'IPTables', 'rules', 'blocking', 'ports', 'required', 'Samba', 'communicate', 'servers'])
    result = list()
    result=g.getAnnotation(5)
    print("\n")
    for i in range(len(result)):
        print("node: "+result[i].name)
        print("PR: %lf"%(result[i].PR[g.IDX]))
    timeEnd = time.time()
    sec = timeEnd - timeStart
    result_list = str(datetime.timedelta(seconds=sec))
    print(result_list)