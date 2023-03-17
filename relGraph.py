import pickle
from cv2 import VideoCapture
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter

from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class vertex:
    def __init__(self, label:int, data:str, segment:int, serial:str):
        #label: 노드의 종류를 나타냄, 1:컴포넌트, 2:비디오 세그먼트, 3:유저
        self.label = label

        #data는 노드의 종류에 따라 내용이 달라진다.
        #1:컴포넌트 이름(위키피디아 타이틀명), 2:영상 제목 or 영상 주소, 3: 유저 id
        self.data = data

        #segment는 노드의 종류가 세그먼트인 경우에만 해당하는 파트 숫자를 입력, 나머지는 0
        self.segment = segment
        self.edgeList = list()

        #neo4j에 노드를 입력하기 편하게 쿼리에들어갈 노드번호를 저장한다.
        self.nodeSerial = serial

class edge:
    def __init__(self, weight):
        #경우에 따라서 가중치대신 세그먼드정보가 들어갈 수 있다.
        self.weight = weight

def getRelGraph(result:list, videoAdress:list):
    #result가 트리플형태로 변환하기 전 이라는 가정으로 시작
    #result: 3차원 리스트, (1)모든 영상에대한 (2)각 세그먼트별 (3)컴포넌트
    #videoAdress: 영상의 주소가 result에 들어있는 순서대로 저장되어있는 리스트
    #
    #딕셔너리 길이 = 16333244
    with open("ComTitleToId.pkl","rb") as inpf:
        title2IdDict = pickle.load(inpf)
    
    #컴포넌트 개수는 딕셔너리 길이와 같다
    #아직 생성되지 않은 노드는 -1
    #최대 id크기 = 70355177
    #id를 다시 시리얼번호를 부여하면 메모리 절약가능
    componentArr = np.zeros(70355178, dtype=int)-1
    
    #컴포넌트 리스트에 추가하면 컴포넌트 배열에 새로 추가되는 컴포넌트의 인덱스를 저장해서 바로 찾을 수 있도록 작성
    componentList = list()
    videoList = list()
    segCount = 0
    videoCount = 0
    vidserial = 0
    for video in result:
        
        for seg in video:
            segCount += 1
            #리스트에 비디오 노드를 추가
            #node4j 테스트용으로 vidserial추가해서 그래프입력할때에 번호 알 수 있게 설정
            videoList.append(vertex(2,videoAdress[videoCount],segCount,"v"+str(vidserial)))
            vidserial+=1
            for compo in seg:
                #구간 별로 컴포넌트 노드 추가

                serial = title2IdDict[compo.encode("utf-8")]
                if componentArr[serial] == -1:#노드 생성
                    #node4j 테스트용으로 시리얼번호 저장
                    n = vertex(1,compo,0, "c"+str(len(componentList)))
                    
                    #생성된 컴포넌트 노드에 비디오노드 연결
                    #컴포넌트 리스트의 인덱스값을 배열에 넣어준다
                    componentArr[serial] = len(componentList)
                    componentList.append(n)

                else:#이미 생성된 컴포넌트
                    n = componentList[componentArr[serial]]

                #컴포넌트 노드와 영상 노드를 연결
                #가중치는 현재 없다고 가정 이후에 상의를 통해 가중치값도 받아서 엣지객체로 만들어 넣어줄것
                n.edgeList.append(videoList[videoCount])
                videoList[len(videoList) - 1].edgeList.append(n)

        videoCount += 1    
        segCount = 0
        

    return componentList, videoList

def visualize(videoList:list, componentList:list):
    g = nx.DiGraph()
    vidNode = list()
    compoNode = list()
    for node in videoList:
        #g.add_node(node.data, color = "r")
        vidNode.append(str(node.data +"_"+ str(node.segment)))

    idList = []
    for node in componentList:
        idList.append(node.data)

    #shell_layout에 필요한 리스트
    #멘션노드와 컨셉노드로 구분
    for node in componentList:
        compoNode.append(node.data)
    shellList = [vidNode,compoNode]

    for node in videoList:
        for edge in node.edgeList:
            g.add_edge(str(node.data +"_"+ str(node.segment)),edge.data)    
    for node in componentList:
        for edge in node.edgeList:
            g.add_edge(node.data,str(edge.data+"_"+ str(edge.segment)))    
    #이분그래프
    nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.bipartite_layout(g,vidNode))

    #순회 그래프, 원형 그래프
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.circular_layout(g))

    #spring
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.spring_layout(g))

    #소용돌이
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.spiral_layout(g))

    #
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.kamada_kawai_layout(g))

    #랜덤
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.random_layout(g))

    #shell
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.shell_layout(g,shellList))

    #자동
    #nx.draw(g, with_labels = True, node_size = 200, font_size = 10)
    plt.show()
class App:
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_graph(self, componantList, videoList):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_graph, componantList, videoList)
            
    @staticmethod
    def _create_graph(tx, componantList, videoList):
        #자체제작 함수

        #모든 컴포넌트 노드 생성
        for componant in componantList:
            query = "CREATE ("+componant.nodeSerial+":KnowledgeComponant { data: $componant_data }) "
            tx.run(query,componant_data = componant.data)

        #모든 비디오 노드 생성    
        for video in videoList:
            query = "CREATE ("+video.nodeSerial+":Video { data: $video_data }) "
            tx.run(query,video_data = video.nodeSerial)

        #비디오노드 순회하면서 비디오노드와 컴포넌트 노드를 연결
        for video in videoList:
            for compo in video.edgeList:
                query = (
                    "MATCH (v: Video {data: $video_data }), (c: KnowledgeComponant {data: $componant_data})"
                    "CREATE (v)-[:Related]->(c)"
                    "RETURN v, c"
                )
                result = tx.run(query,video_data = video.nodeSerial, componant_data = compo.data)
                
                #비디오노드와 컴포넌트 노드 연결시키면서 콘솔창에 출력
                try:
                    for row in result:
                        print("Created relationship between video:{v}, componant:{c}".format(
                        v=row["v"]["data"], c=row["c"]["data"]))
                
                # Capture any errors along with the query and data for traceability
                except ServiceUnavailable as exception:
                    logging.error("{query} raised an error: \n {exception}".format(
                        query=query, exception=exception))
                    raise

    def find_person(self, person_name):
        with self.driver.session(database="neo4j") as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]

    def delete_all_data(self):
        with self.driver.session(database="neo4j") as session:
            result = session.read_transaction(self._delete_all_node_and_relationship)
    
    @staticmethod
    def _delete_all_node_and_relationship(tx):
        query = (
            "match (a) optional match (a)-[r]-() delete a, r"
        )
        tx.run(query)

if __name__ == '__main__':   
    #그래프 만드는거 테스트
    #r: 각 영상별 세그먼트별 knowledge componant리스트(3차원 리스트)
    
    r = [[['Huilongguan', 'Huilongguan', 'Huilongguan', 'Huilongguan', 'Huilongguan'], ['Girolamo_Tartarotti', 'Girolamo_Tartarotti', 'Girolamo_Tartarotti', 'Girolamo_Tartarotti', 'Girolamo_Tartarotti'], ['A', 'A', 'A', 'A', 'A'],['A', 'A', 'A', 'A', 'A']],
    [['Bread', 'Bread', 'Bread', 'Bread', 'Bread'], ['Bread', 'Bread', 'Bread', 'Bread', 'Bread'], ['Staple_food', 'Staple_food', 'Staple_food', 'Staple_food', 'Staple_food'], ['Staple_food', 'Staple_food', 'Staple_food', 'Staple_food', 'Staple_food']],
    [['Meat', 'Meat', 'Meat', 'Meat', 'Meat'], ['Meat', 'Meat', 'Meat', 'Meat', 'Fat'],['Fat', 'Fat', 'Fat', 'Fat', 'Fat']],
    [['Ester', 'Glyceride', 'Vegetable_oil', 'Olive_oil', 'Candy_cigarette'], ['Ester', 'Glyceride', 'Vegetable_oil', 'Olive_oil', 'Popeye']],
    [['Ester', 'Glyceride', 'Vegetable_oil', 'Popeye', 'Candy_cigarette'], ['Ester', 'Glyceride', 'Popeye', 'Candy_cigarette', 'Candy'], ['Ester', 'Vegetable_oil', 'Olive_oil', 'Popeye', 'Candy_cigarette']],
    [['Confectionery', 'Confectionery', 'Sweetbread', 'Pork', 'Cooking'], ['Confectionery', 'Sweetbread', 'Pork', 'Cooking', 'Oven']]]
    
    #vl: 영상의 링크 혹은 제목의 리스트
    vl = ['vid1', 'vid2', 'vid3', 'vid4', 'vid5', 'vid6']
    
    #관계 그래프 작성
    cl, vvl = getRelGraph(r,vl)
    
    # Aura queries use an encrypted connection using the "neo4j+s" URI scheme
    uri = "neo4j+s://8a488d74.databases.neo4j.io"
    user = "neo4j"
    password = "nZjn1bV_6nEPqDMs6l4f5rAnOo81peh7osW0X5fjcVw"
    app = App(uri, user, password)
    #app.delete_all_data()
    app.create_graph(cl,vvl)
    app.close()
