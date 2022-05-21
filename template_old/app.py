#--------------------------------------------------------------------------------#flask
from tkinter.messagebox import NO
from flask import Flask, render_template, request, jsonify, redirect, url_for 
#-------------------------------------------------------------------------------#
import requests
from bs4 import BeautifulSoup
#--------------------------------------------------------------------------------------
app = Flask(__name__)
#--------------------------------------------------------------------------------------
class videoText():
	def __init__(self, longString):
		self.words = longString.split()
		self.head = 0
	def pop(self):
		word = self.words[self.head]
		self.head += 1
		return word
	def empty(self):
		if self.head == len(self.words):
			return True
		else:
			return False
#--------------------------------------------------------------------------------------	
def urlToSoup(url):
	req = requests.get(url)
	soup = BeautifulSoup(req.text, 'lxml')
	return soup
#검색이 되는것만 넣기로함?????
#겹치는걸 방지하기로 함
#그래서 딕셔너리에 넣고 나중에 리스트로 반환
def wikification(longString):
	retWords = []#[문장에 나온 단어1, 문장에 나온 단어2 ..]
	retLinks = []#[[[문장에 나온 단어 1을 검색해서 나온 링크 단어1, ~를 검색해서 나온 링크 단어 갯수], [문장에 나온 단어 1을 검색해서 나온 링크 단어2, ~를 검색해서 나온..]],
	vt = videoText(longString)
	while not vt.empty():
		word = vt.pop()
		soup = urlToSoup('https://en.wikipedia.org/wiki/' + word)
		tag = soup.select_one('#noarticletext > tbody > tr > td > b')
		if tag is None:
			retWords.append(word)#return ready
			#오류 태그가 존재하지 않으면
			dictLinks = {}
			tag = soup.select_one('#mw-content-text')
			tags = tag.select("a[href^='/wiki/']")
			for tag in tags:
				#중복되지 않았다면, (명확성 안내 링크 삭제, ?자기이름 링크 삭제?, 파일이 아니면, 와! 놀랍게도 세미콜론 들어가는거만 빼주면 될거같다!)
				if (tag.text not in dictLinks)and(':' not in tag['href']):
					dictLinks[tag.text] = 0

			#~
			retLinks.append(list(zip(dictLinks.keys(), dictLinks.values())))#return ready
	print("end")
	return retWords, retLinks
#--------------------------------------------------------------------------------------

@app.route("/")
def index():
	return render_template('index.html')
s=""
@app.route("/start", methods=['POST'])
def start():
	global s
	j = request.json#main->longStringing=>json->j
	longString = j['longString']
	inputWords, inputWordsWFC = wikification(longString)
	#임시
	s = "입력 문장에서 총 "+str(len(inputWords))+"개의 문장 감지\n"
	i = 0
	for word in inputWords:
		s += (word + "링크 " + str(len(inputWordsWFC[i]))+'개 : \n')
		for info in inputWordsWFC[i]:
			s += (' ㄴ ' + info[0] + ' : ' + '0' + '\n')
		s += '\n\n'
		i += 1
	return "a"
	#return redirect(url_for('index'))
@app.route("/res", methods=['POST'])
def res():
	global s
	r = s.replace('\n','<br>')
	test_data = {"s" : r}
	return jsonify(test_data)
#--------------------------------------------------------------------------------------
if __name__ == "__main__":
		app.debug = True
		app.run(debug=True)