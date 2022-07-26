import pickle as pic
import numpy as np

def ready(local):
    SPLIT_PROCESS = 3 # +1
    banList = set([':', '<', '>', '|'])
    QUESTION = "~Q~"
    SLASH = "~S~"
    STAR = "~Z~"
    DOT = "~D~"
    REVERS_SLASH = "~R~"
    DOUBLE_DOT = "~P~"
    SINGLE_DOT = "~O~"
    nameIDToTitle = local + 'ComIDToTitle.npy'
    nameTitleToID = local + 'ComTittleToID.pkl'
    nameAnchorText = local + 'Arr1.pkl'
    nameAnchorTargetID = local + 'Arr2.pkl'
    nameNowPageID = local +'Arr3.pkl'
    nameBack = local + 'backlinks/'
    namePr0den = local + 'pr0dens/'

    ret1_idToTitle = np.load(nameIDToTitle, allow_pickle=True)
    with open(nameTitleToID,'rb') as f:
        ret2_titleToId = pic.load(f)
    with open(nameAnchorText, 'rb') as f:
        ret3_listAnchorText = pic.load(f)
    with open(nameAnchorTargetID, 'rb') as f:
        ret4_listAnchorTargetID = pic.load(f)
    with open(nameNowPageID, 'rb') as f:
        ret5_listNowPageID = pic.load(f)
    return ret1_idToTitle, ret2_titleToId, ret3_listAnchorText, ret4_listAnchorTargetID, ret5_listNowPageID