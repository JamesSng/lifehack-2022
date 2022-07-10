import awstools

import gensim
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import enchant
import math
import random
def pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:         
        return None


def clean_text(text):
    d1 = enchant.Dict("en_US")
    d2 = enchant.Dict("en_GB")
    
    words = stopwords.words('english')
    
    lemmatizer = WordNetLemmatizer()
    
    text = text.lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))

    arr = text.split()
    new_arr = []
    for k in range(len(arr)):
        if arr[k] not in words and len(arr[k])>1 and(d1.check(arr[k]) or d2.check(arr[k])):
            p = pos_tagger(nltk.pos_tag([arr[k]])[0][1])
            if(p==None):
                new_arr.append(lemmatizer.lemmatize(arr[k]))
            else:
                new_arr.append(lemmatizer.lemmatize(arr[k], p))

    text = ' '.join(new_arr)
    return ''.join([c for c in text if ord(c)<128])


def tokenize_text(text):
    tokens = []
    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if len(word) < 2:
                continue
            tokens.append(word.lower())
    return tokens


def get_events():
    events = awstools.getAllEvents() 
    arr = []
    model = gensim.models.KeyedVectors.load_word2vec_format('model/GoogleNews-vectors-negative300.bin', binary=True, limit=50000)
    for event in events:
        text = clean_text(event['description'])
        words = tokenize_text(text)
        vector = [0] * 300
        sze = 0
        for word in words:
            if word in model:
                tmp = model[word]
                sze += 1
                for i in range(len(tmp)):
                    vector[i] += tmp[i]
        if sze > 0:
            for i in range(300):
                vector[i] /= sze
        arr.append([event['eventid'], event['description'], vector])
    df = pd.DataFrame(arr, columns=['id', 'description', 'vector'])
    df = df.set_index('id')
    return df


def suggest_similar(eventid):
    df = get_events()
    lst = []
    for index, row in df.iterrows():
        if index == eventid:
            continue
        dist = math.dist(df.loc[eventid, 'vector'], row['vector'])
        lst.append((dist,index))
    lst.sort()
    names = []
    for x in lst:
        names.append(x[1])
    return names
"""
def suggest_user(userid):
    arr = [x['eventid'] for x in awstools.getEventsFromVolunteer(userid)]
    df = get_events()
    lst = []
    for index, row in df.iterrows():
        if index in arr:
            continue;
        mn = 1000000005
        for event in arr:
            dist = math.dist(row['vector'], df.loc[event, 'vector'])
            print(index, event, dist)
            mn = min(mn, dist)
        print(index, mn)
        lst.append((mn, index))
    lst.sort()
    names = []
    for x in lst:
        names.append(x[1])
    return names
        
"""

def suggest_user(userid):
    arr=[x['eventid'] for x in awstools.getEventsFromVolunteer(userid)]
    df=get_events()
    
    vector = [0]*300
    names=[]
    for index,row in df.iterrows():
        if index in arr:
            for i in range(300):
                vector[i]+=row['vector'][i]
        else:
            names.append(index)
    if len(arr)==0:
        random.shuffle(names)
        return names
    for i in range(300):
        vector[i]/=len(arr)
    lst=[]
    for i in names:
        dist=math.dist(df.loc[i,'vector'],vector)
        lst.append((dist,i))
    lst.sort()
    names=[]
    for x in lst:
        names.append(x[1])
    return names


if __name__ == '__main__':
    username = input('Username: ')
    print(suggest_user(username))

