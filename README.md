<div align="center">

<h1>Automated construction of concept maps from massive online educational videos</h1>
대규모 온라인 강의비디오로부터 컨셉 맵을 자동으로 구축하는 방법

![d](https://img.shields.io/badge/-Python3-3776AB?style=flat-square&logo=python&logoColor=FFFFFF) ![d](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=FFFFFF)  ![d](https://img.shields.io/badge/-Javascript-F7DF1E?style=flat-square&logo=javascript&logoColor=FFFFFF) 

</div>

## Description
방대한 양의 강의 영상이 온라인 비디오 공유 플랫폼(예, Youtube)에서 이용가능함에 따라, 학습자는 비디오 내 정보를 효과적으로 구조화 및 조직화하길 원한다. 컨셉 맵(Concept map)은 정보에 대한 구조화되고 조직화된 개념적인 표현이며, 학습자의 학습과정을 효율적, 효과적으로 보조하는 도구로 널리 사용되고 있다. 하지만, 상당 수의 컨셉 맵의 생성과정은 사람의 의한 수동적인 작업이거나 생성되는 컨셉 맵은 비디오 내 텍스트에만 의존하기 때문에 의미적으로 결여되어 있다. 이로 인해, 기존의 생성과정은 매우 높은 비용을 요구되고 생성된 개념 맵은 모호한 정보를 포함합니다.

이러한 문제를 해결하기 위해, 우리는 강의 영상로부터 컨셉 맵을 자동으로 구성한다. 주요 기술적 특징은 다음과 같다.
- Wikipedia의 방대한 지식 데이터를 바탕으로 컨셉 맵의 생성을 실시간으로 수행합니다
- Youtube의 강의 영상 URL과 제공되는 사용자-정의 옵션을 통해, 다양한 형태의 컨셉 맵이 생성됩니다
- 모호성(Disambiguation) 식별과 추출된 개념간의 긴말한 관계 계산(Computation of strong relationships)은 향상된 [Page Rank](https://en.wikipedia.org/wiki/PageRank) 알고리즘을 기초로 합니다.
- Docker를 통해 가상화된 컨테이너 제공을 통해 손쉬운 설치가 가능합니다.

## Product demo video

<div align="center">

![01](https://user-images.githubusercontent.com/24387014/209906029-d1b0ae5b-fd30-4fbd-8811-15f9377fd43d.gif)

</div>

해당 서비스는 [Project-ROKC](https://github.com/BonhyeonGu/Project-ROKC)의 일부분 입니다.

## Installation and execution
우리 서비스는 두 종류(Docker container and bare metal)의 설치 및 실행 방법을 제공하며,  `Docker` 컨테이너를 통한 설치 및 실행을 적극 추천합니다. 

### Docker container

reposit에 동봉된 Dockerfile, [docker-compose](https://docs.docker.com/compose/install/)로 컨테이너로 설치하여 사용 가능합니다.  
workspace 내에서 아래의 명령어를 입력하고 http://127.0.0.1:5050 으로 접속 가능합니다.

```bash
docker-compose up -d
```

해당 도커파일은 빌드시 dump된 파일들을 github에서 내려받습니다. 따라서 인터넷이 되는 환경에서만 빌드가 가능하며  
약 한 시간의 시간이 소요될 수 있습니다.

### Bare metal

#### Installation 

해당 프로그램은 아래의 추가적 Python Module들을 필요로 합니다.

 - flask
 - youtube-transcript-api
 - beautifulsoup4
 - lxml
 - numpy
 - nltk (추가 설치 필요, workspace 내부의 nltk_install.py로 처리할 수 있습니다.)
 - matplotlib
 - networkx

해당 프로그램은 큰 자료구조를 상시 머물게 하며 작동됩니다. 따라서 최소 아래의 사양이 필요합니다.
 - RAM : 16GB
 - Workspace : 20GB (실행 케이스에 따라 더 필요할 수 있음)

다음은 자료구조를 Dump한 파일들이 필요합니다. 해당 reposit의 [Releases](https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases)에서 확인 가능합니다.  
모두 내려받은 후 workspace에 넣습니다.  
'backlinksZip.7z' 는 분할 압축 되어있으니 압축을 풀고 내용만 workspace 내에 위치하면 되며, 압축파일은 삭제해도 무방합니다.

다음은 workspace 내에 driectory 두 개를 다음 이름으로 생성합니다.

 - pr0dens
 - backlinks

이후 workspace내부의 unzipBacklinks.py를 실행합니다. all_clear가 출력되어야 완료되었음을 나타냅니다. 이 작업이 완료되면 driectory-backlinks가 채워진 것을 확인할 수 있습니다.

아래는 준비가 완료되었을 때의 조회입니다. ('nohup.out'은 linux background가 생성함)
![clear](https://user-images.githubusercontent.com/24387014/184473483-f47834f2-b9d6-45a7-82db-23885925cdd0.PNG)

#### Execution: WebApp

workspace 내부의 app.py로
```bash
flask run
```
을 통하여 웹 서비스를 실행할 수 있습니다.  
http://127.0.0.1:5050 으로 접속 가능합니다.

## Additional information

### Extracting concepts

workspace 내부의 ComponentExtractor.py을 edit open하여 92번째 줄을 주석 해제합니다.  
해당 메소드의 각 인자는 youtube url, Second of Second of Split Segmen를 뜻합니다. 원하는 대로 edit 후 open된 ComponentExtractor.py 자체를 실행합니다.  
KnowledgComponent 가 Buffer에 출력됩니다.

주의 : 만약 다시 Web Service로 Run 하고 싶다면 해당 92번째 줄을 다시 주석처리 해주어야 합니다.

### Visualizating a network of concepts

workspace 내부의 MC_Graph.py을 edit open하여 __414번째 줄__을 주석 해제합니다. 해당 작업은 위의 *Only Find KnowledgComponent*와 함께 쓰시는 것을 권장드립니다.
종료되면 matplotlib와 networkx를 통해 Graph Window가 나타납니다.

<div align="center">

![Graph](https://user-images.githubusercontent.com/24387014/184474406-7c54a7dd-c561-4a59-aa17-4432bc2ad887.jpeg)

</div>

또는 visualizeGraph.py에서 그래프 모양을 설정할 수 있습니다.

주의 : 해당 작업은 출력 생성과 출력을 살펴보려는 시도에서 Over head가 지속적으로 발생합니다.


## Quick start

<div align="center">

![02_Tuto](https://user-images.githubusercontent.com/24387014/184350805-697abed0-3e3c-4a21-bea5-7bc2b150685d.png)

</div>

### 1. Typing a Youtube URL to generate its concept map

유튜브 동영상의 URL 주소를 입력합니다. 단 유튜브 공식 기능의 **영어 자막이 존재하는 영상**이여야 합니다.

### 2. Define an interval of a video segment (default: 300.0 seconds)

Segment를 나눌 기준이 되는 시간(초)를 정의합니다.
만약 자막의 시간 범위가 여기서 정의한 기준을 가로지르는 경우 해당 자막은 두 Segment Knowledge Component 모두 영향을 끼치게 됩니다.

예를 들어 해당 값이 300.0초이고 자막이 영상의 14분 55초 부터 15분 02초에 종료된다면
해당 자막은 세번째, 네번째 Segment에 영향을 끼칩니다.

### 3. Specify how many concepts are extracted in each segment (default: 5 concepts)

하나의 Segment에 몇개의 Knowledge Component를 추출할 것인지에 대한 정의입니다.

### 4. Check if concepts are distinct or not in an entire video (default: false)

자막 속 Mention들을 계속해서 반영하게 되면, 단어를 중복적으로 연결짓게 됩니다. 이는 결과가  Mention의 등장 횟수와 연관됩니다.
만약 해당 값을 False로 정의한다면, 한 Segment속에 동일한 Mention이 접수될 때 필터링 됩니다. 

### 5. Check if the output format of concepts are encoded in RDF triples or not (default: RDF triple)
	
결과를 보기 편하게 Knowledge Component 형식으로 표시하거나 Triple 형식으로 출력하기를 결정합니다.
Triple 타입은 다음 프로젝트에 사용할 예정입니다.

<div align="center">

![3_TripleOrTuple](https://user-images.githubusercontent.com/24387014/184352041-729f6567-39bb-41a8-bda4-c1e31367badb.png)

</div>


## Citation
If you find our application useful in your work, and you want to cite our work, please use the following reference:

## License
```
```
