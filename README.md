<div align="center">

<h1>Reasoning over Knowledge Component Streams</h1>

![d](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=FFFFFF) ![d](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=FFFFFF)  ![d](https://img.shields.io/badge/-JS-F7DF1E?style=flat-square&logo=javascript&logoColor=FFFFFF) 

</div>

## Overview

<div align="center">

![01_Over](https://user-images.githubusercontent.com/24387014/184350904-12adecf5-0adb-498d-922d-a8c8da9bf513.gif)

</div>

유튜브 영상의 Knowledge Component를 출력하는 프로그램입니다.
대부분 처리하기 위해 미리 가공된 Wikipedia Data를 사용하며 오직 하나의 속성만 크롤링, 캐싱합니다.

##

## How to Install

해당 프로그램은 아래의 추가적 Python Module들을 필요로 합니다.

 - flask
 - youtube-transcript-api
 - beautifulsoup4
 - lxml
 - numpy
 - nltk (추가 설치 필요, Workspace 내부의 nltk_install.py로 처리할 수 있습니다.)
 - matplotlib
 - networkx

해당 프로그램은 큰 자료구조를 상시 머물게 하며 작동됩니다. 따라서 최소 아래의 사양이 필요합니다.
 - RAM : 16GB
 - Workspace : 20GB

다음은 자료구조를 Dump한 파일들이 필요합니다. 해당 Reposit의 [Releases](https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases)에서 확인 가능합니다.  
모두 내려받은 후 Workspace에 넣습니다.  
'backlinksZip.7z' 는 분할 압축 되어있으니 압축을 풀고 내용만 Workspace 내에 위치하면 되며, 압축파일은 삭제해도 무방합니다.

다음은 Workspace 내에 driectory 두 개를 다음 이름으로 생성합니다.

 - pr0dens
 - backlinks

이후 Workspace내부의 unzipBacklinks.py를 실행합니다. all_clear가 출력되어야 완료되었음을 나타냅니다. 이 작업이 완료되면 driectory-backlinks가 채워진 것을 확인할 수 있습니다.

아래는 준비가 완료되었을 때의 조회입니다. ('nohup.out'은 linux background가 생성함)
![clear](https://user-images.githubusercontent.com/24387014/184473483-f47834f2-b9d6-45a7-82db-23885925cdd0.PNG)

## How to Run

### Run : Web Service

Workspace 내부의 app.py로 flask run 명령어를 통하여 웹 서비스를 실행할 수 있습니다.  
http://127.0.0.1:5050 으로 접속 가능합니다.

### Debug : Only Find KnowledgComponent

Workspace 내부의 ComponentExtractor.py을 edit open하여 92번째 줄을 주석 해제합니다.  
해당 메소드의 각 인자는 youtube url, Second of Second of Split Segmen를 뜻합니다. 원하는 대로 edit 후 open된 ComponentExtractor.py 자체를 실행합니다.  
KnowledgComponent 가 Buffer에 출력됩니다.

주의 : 만약 다시 Web Service로 Run 하고 싶다면 해당 92번째 줄을 다시 주석처리 해주어야 합니다.

### Debug : Visualization Graph

Workspace 내부의 MC_Graph.py을 edit open하여 **414번째 줄**을 주석 해제합니다. 해당 작업은 위의 *Only Find KnowledgComponent*와 함께 쓰시는 것을 권장드립니다.
종료되면 matplotlib와 networkx를 통해 Graph Window가 나타납니다.

<div align="center">

![Graph](https://user-images.githubusercontent.com/24387014/184474406-7c54a7dd-c561-4a59-aa17-4432bc2ad887.jpeg)

</div>

또는 visualizeGraph.py에서 그래프 모양을 설정할 수 있습니다.

주의 : 해당 작업은 출력 생성과 출력을 살펴보려는 시도에서 Over head가 지속적으로 발생합니다.

## Tutorial

<div align="center">

![02_Tuto](https://user-images.githubusercontent.com/24387014/184350805-697abed0-3e3c-4a21-bea5-7bc2b150685d.png)

</div>

### 1. Youtube URL

유튜브 동영상의 URL 주소를 입력합니다. 단 유튜브 공식 기능의 **영어 자막이 존재하는 영상**이여야 합니다.

### 2. Second of Split Segment  (Default 300.0)

Segment를 나눌 기준이 되는 시간(초)를 정의합니다.
만약 자막의 시간 범위가 여기서 정의한 기준을 가로지르는 경우 해당 자막은 두 Segment Knowledge Component 모두 영향을 끼치게 됩니다.

예를 들어 해당 값이 300.0초이고 자막이 영상의 14분 55초 부터 15분 02초에 종료된다면
해당 자막은 세번째, 네번째 Segment에 영향을 끼칩니다.

### 3. Number of Knowledge Component (Default 5)

하나의 Segment에 몇개의 Knowledge Component를 확보할 것인지에 대한 정의입니다.

### 4. Whether of Calculate Hit Count (Default False)

자막 속 Mention들을 계속해서 반영하게 되면, 단어를 중복적으로 연결짓게 됩니다. 이는 결과가  Mention의 등장 횟수와 연관됩니다.
만약 해당 값을 False로 정의한다면, 한 Segment속에 동일한 Mention이 접수될 때 필터링 됩니다. 

### 5. Whether of Output Structure (Default Triple)

결과를 보기 편하게 Knowledge Component 형식으로 표시하거나 Triple 형식으로 출력하기를 결정합니다.
Triple 타입은 다음 프로젝트에 사용할 예정입니다.

<div align="center">

![3_TripleOrTuple](https://user-images.githubusercontent.com/24387014/184352041-729f6567-39bb-41a8-bda4-c1e31367badb.png)

</div>
