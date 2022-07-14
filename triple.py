import random
class Triple:
    def getPartNumber(self, result:list):
        #딕셔너리로 각 컴포넌트별로 몇번파트에 등장했는지 기록
        #key=컴포넌트, value=등장한 파트번호를 기록한 리스트
        compo = dict()
        part = 1
        #result는 2차원리스트
        for t in result:
            #t는 result중 하나의 리스트
            for i in t:
                #i는 컴포넌트
                try:
                    compo[i].append(part)
                except KeyError:
                    compo[i]=list()
                    compo[i].append(part)
            part+=1
        return self.mergePartNumber(compo)
        
    def mergePartNumber(self, compo:dict):
    #연속된 파트번호 병합 시작
        for key in compo:
            print(key)
            start = -2
            end = -2
            cnt=0

            #딕셔너리의 value인 리스트자체를 바꿔줄때 쓸 리스트
            l = list()

            for now in compo[key]:
                if (cnt == 0):
                    start = now
                    end = now
                elif (now - end == 1):
                    end = now
                elif (now-end > 1):
                    if(start == end):
                        l.append(str(end))
                    else:
                        l.append(str(start) + "-" + str(end))
                    start = now
                    end = now
                cnt += 1
            if(start == end):
                l.append(str(end))
            else:
                print(str(start) + "-" + str(end))
                l.append(str(start) + "-" + str(end))
            
            compo[key] = l

        return compo

    def output(self, d2list):
        n = random.randrange(1,100000)
        ziip = self.getPartNumber(d2list)
        ret_s1 = []
        ret_s2 = []
        ret_s3 = []
        for key, value in ziip.items():
            s1 = '< :v%d :hasKnowledgeComponent dbr:'%(n)
            s3 = ' %s >'%(value)
            s3 = s3.replace('\'', '')
            s3 = s3.replace('[', '<')
            s3 = s3.replace(']', '>')
            ret_s1.append(s1)
            ret_s2.append(key)
            ret_s3.append(s3)
        return ret_s1, ret_s2, ret_s3
