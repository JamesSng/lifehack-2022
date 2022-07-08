import awstools

import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

import enchant

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


def get_events():
    events = awstools.getAllEvents() 
    df = pd.DataFrame(['a', 'b'], columns=['id', 'description'])
    for event in events:
        df = df.append(pd.DataFrame([event['eventid'], event['description']], columns=['id', 'description']))
    print(df)


if __name__ == '__main__':
    get_events()

