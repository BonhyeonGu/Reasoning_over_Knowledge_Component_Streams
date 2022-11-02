import networkx as nx
import matplotlib.pyplot as plt
from fileIO import FileIO
def listToDict(vertexList:list, idList:list):
    d=dict()
    i=0
    for vertex in vertexList:
        d[vertex.name]=idList[i].decode('utf-8')
        i+=1
    return d

def visualize(mentionList:list, conceptList:list):
    fileIO = FileIO()
    g = nx.DiGraph()
    mentionNode = list()
    conceptNode = list()
    for node in mentionList:
        g.add_node(node.name, color = "r")
        mentionNode.append(node.name)

    idList = []
    for node in conceptList:
        idList.append(int(node.name))
    idList = fileIO.getIDToTitle(idList)
    
    idDict = listToDict(conceptList,idList)

    #shell_layout에 필요한 리스트
    #멘션노드와 컨셉노드로 구분
    for node in conceptList:
        conceptNode.append(idDict[node.name])
    shellList = [mentionNode,conceptNode]

    for node in mentionList:
        for edge in node.edges:
            g.add_edge(edge.start.name,idDict[edge.dest.name])    
    for node in conceptList:
        for edge in node.edges:
            g.add_edge(idDict[edge.start.name],idDict[edge.dest.name])
    #이분그래프
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.bipartite_layout(g,mentionNode))

    #순회 그래프, 원형 그래프
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.circular_layout(g))

    #spring
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.spring_layout(g))

    #소용돌이
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.spiral_layout(g))

    #
    nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.kamada_kawai_layout(g))

    #랜덤
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.random_layout(g))

    #shell
    #nx.draw(g, with_labels = True,node_size = 200, font_size = 10, pos=nx.shell_layout(g,shellList))

    #자동
    #nx.draw(g, with_labels = True, node_size = 200, font_size = 10)
    plt.show()