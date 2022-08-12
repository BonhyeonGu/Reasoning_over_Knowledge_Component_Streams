<div align="center">

<h1>Reasoning over Knowledge Component Streams</h1>

![d](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=FFFFFF) ![d](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=FFFFFF)  ![d](https://img.shields.io/badge/-JS-F7DF1E?style=flat-square&logo=javascript&logoColor=FFFFFF) 

</div>

## Overview

![01_Over](https://user-images.githubusercontent.com/24387014/184350904-12adecf5-0adb-498d-922d-a8c8da9bf513.gif)

유튜브 영상의 Knowledge Component를 출력하는 프로그램입니다.
대부분 처리하기 위해 미리 가공된 Wikipedia Data를 사용하며 오직 하나의 속성만 크롤링, 캐싱합니다.

## How to Install

준비된 Dumpfile들이 필요합니다. 아래의 Reposit에서 확인 바랍니다.

[DumpMaker](https://github.com/BonhyeonGu/DUMPMAKER-Reasoning_over_Knowledge_Component_Streams)

또한 아래의 하이라키대로 준비해야 합니다.

사진2

해당 프로그램은 아래의 추가적 Python Module들을 필요로 합니다.

 - flask
 - youtube-transcript-api
 - beautifulsoup4
 - lxml
 - numpy
 - nltk (추가 설치 필요)
 - matplotlib
 - networkx

## Tutorial

![03_Tuto](https://user-images.githubusercontent.com/24387014/184350805-697abed0-3e3c-4a21-bea5-7bc2b150685d.png)

### 1. Youtube URL

​유튜브 동영상의 URL 주소를 입력합니다. 단 유튜브 공식 기능의 **영어 자막이 존재하는 영상**이여야 합니다.

### 2. Second of Split Segment  (Default 300.0)

Segment를 나눌 기준이 되는 시간(초)를 정의합니다.
만약 자막의 시간 범위가 여기서 정의한 기준을 가로지르는 경우 해당 자막은 두 Segment Knowledge Component 모두 영향을 끼치게 됩니다.

예를 들어 해당 값이 300.0초이고 자막이 영상의 14분 55초 부터 15분 02초에 종료된다면
해당 자막은 세번째, 네번째 Segment에 영향을 끼칩니다.

### 3. Number of Knowledge Component (Default 5)

하나의 Segment에 몇개의 Knowledge Component를 확보할 것인지에 대한 정의입니다.

### 4. Whether of Calculate Hit Count (Default False)

자막 속 Mention들을 계속해서 반영하게 되면, 단어를 중복적으로 연결짓게 됩니다. 이는 결과가  Mention의 등장 횟수와 연관됩니다.
만약 해당 값을 False로 정의한다면, 한 Segment속에 동일한 Mention이 접수되면 필터링 됩니다. 

### 5. Whether of Output Structure (Default Triple)

결과를 보기 편하게 Knowledge Component 형식으로 표시하거나 Triple 형식으로 출력하기를 결정합니다.
Triple 타입은 다음 프로젝트에 사용할 예정입니다.

사진4