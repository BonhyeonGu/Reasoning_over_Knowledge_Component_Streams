import numpy as np
def concatening(token:list, wordLength:int):#token: tokenize한 단어들, wordLength: 합칠 단어의 최대 개수
    li = []
    for i in range(wordLength):
        li.append("")
    arr = np.array(li,dtype='object')
    ans = list()
    ansAppend = ans.append
    

    #초기 구간
    j = 1
    for word in token[:wordLength]:
        for i in range(j):
            if len(arr[i]) > 0:
                arr[i] += "_"+word 
            else:
                arr[i]=word
            ansAppend(arr[i])

        j+=1
    arr[0] = ""
    #초기구간 이후
    reset_idx = 1
    for word in token[wordLength:]:
        for i in range(wordLength):
            if len(arr[i]) > 0:
                arr[i] += "_"+word 
            else:
                arr[i]=word
            ansAppend(arr[i])
        
        arr[reset_idx]=""
        reset_idx = (reset_idx+1)%wordLength

    return ans
