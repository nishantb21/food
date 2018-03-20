from collections import Counter, defaultdict
from sklearn.metrics import mean_squared_error
import sys
import json
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import time
import pickle
import csv

my_path = os.path.abspath(os.path.dirname(__file__))


def tokenize_string(my_string):
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(db):
    """
    The meta tags associated with each dish is broken down (tokenized) as a list of tags
    Eg: egg|flour|ghee|paratha will be tokenized as [egg, flour, ghee, paratha]
    """
    tokenlist=[]
    for index,row in db.iterrows():
        tokenlist.append(tokenize_string(row.tags))
    db['tokens']=tokenlist
    return db

def featurize(db):
    """
    Each row will contain a csr_matrix of shape (1, num_features).
    Each entry in this matrix will contain the tf-idf value of the term
    Formula : tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document 
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents 
    """
    def tf(word, doc):
        return doc.count(word) / Counter(doc).most_common()[0][1]

    def df(word, doclist):
        return sum(1 for d in doclist if word in d)

    def tfidf(word, doc, dfdict, N):
        return tf(word, doc) * math.log10((N / dfdict[word]))

    def getcsrmatrix(tokens,dfdict,N,vocab):
        matrixRow_list = []
        matrixRow_list = np.zeros((1,len(vocab)),dtype='float')
        for t in tokens:
            if t in vocab:
                matrixRow_list[0][vocab[t]] = tfidf(t,tokens,dfdict,N)
        return csr_matrix(matrixRow_list)

    N=len(db)
    doclist = db['tokens'].tolist()
    vocab = { i:x for x,i in enumerate(sorted(list(set(i for s in doclist for i in s)))) }

    dfdict = {}
    for v in vocab.items():
        dfdict[v[0]] = df(v[0],doclist)

    csrlist = []
    for index, row in db.iterrows():
         csrlist.append(getcsrmatrix(row['tokens'],dfdict,N,vocab))

    db['features'] =  csrlist
    return (db,vocab)


def my_train_test_split(ratings):
    """
    Returns a random split of the ratings matrix into a training and testing set.
    """

    test = set(range(len(ratings))[::20])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]

def cosine_sim(a, b):
    """
    """

    v1 = a.toarray()[0]
    v2  = b.toarray()[0]
    return sum(i[0] * i[1] for i in zip(v1, v2))/(math.sqrt(sum([i*i for i in v1]))*math.sqrt(sum([i*i for i in v2])))

def make_predictions(db, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, prediction is made on the ratings for each
    row in ratings_test.
    This is done by computing the weighted average
    rating for every other dish that the user has rated.
    """

    result = []
    for index,row in ratings_test.iterrows():
        mlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['dishId'])
        csrlist = list(db.loc[db['dishId'].isin(mlist)]['features'])
        mrlist = list(ratings_train.loc[ratings_train['userId'] ==row['userId']]['rating'])
        sim = [cosine_sim(c,db.loc[db['dishId'] ==row['dishId']]['features'].values[0]) for c in csrlist]
        wan = sum([ v*mrlist[i] for i,v in enumerate(sim) if v>0 ])
        wadlist = [i for i in sim if i>0]
        if (len(wadlist)>0):
            result.append(wan/sum(wadlist))
        else:
            result.append(np.mean(mrlist))
    return np.array(result)

def main(data, db, predict_on):
    """
    """
    total_dishes = db.shape[0]

    db = tokenize(db)
    db, vocab = featurize(db)
    
    ratings_train, ratings_test = my_train_test_split(data)

    predictions = make_predictions(db, ratings_train, ratings_test)

    predicted_test_error = mean_squared_error(ratings_test.rating, predictions) ** 0.5

    def predict_on_user(predict_on):
        ratings_test = pd.DataFrame(columns = ['userId', 'dishId'])
        ratings_test['userId'] = [predict_on] * total_dishes
        ratings_test.dishId = range(1, total_dishes + 1)
           
        predictions_uid = make_predictions(db, ratings_train, ratings_test)

        predictions_uid = list(enumerate(predictions_uid))

        predictions_uid = sorted(predictions_uid, key = lambda x: x[1], reverse = True)

        predictions_uid = list(map(lambda x: (x[0] + 1, x[1]), predictions_uid))

        return predictions_uid

    return (predicted_test_error, predict_on_user(predict_on = predict_on))
    

def start(predict_on = 100):
    data = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/review.csv'))
    data = data[data['userId'].isin(data['userId'].value_counts()[data['userId'].value_counts() >= 5].index)]    
    db = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/database.csv'), names = ['dishId', 'tags'])
    dishes = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/id_name_mapping.csv'), names = ['dishId', 'dish_name'])

    time_start = time.time()

    predicted_test_error, predictions = main(data, db, predict_on = predict_on)
    
    predictions = pd.DataFrame(predictions, columns = ['dishId', 'rating'])
    predictions = predictions.merge(dishes, on = 'dishId', how = 'left')
    prediction = predictions[['dish_name', 'rating']]
    predicted_rating = prediction.to_dict(orient = 'records')[:10]

    data = data[data.userId == predict_on]
    original_rating = data.merge(predictions, how = 'left', on = 'dishId')
    original_rating.columns = ['userId', 'dishId', 'original_rating', 'predicted_rating', 'dish_name']
    original_rating = original_rating[['dish_name', 'original_rating', 'predicted_rating']]
    original_rating = original_rating.to_dict(orient = 'records')
    
    time_end = time.time()

    answer = {"user" : predict_on, "predicted_test_error": round(predicted_test_error, 2), "time" : round(time_end - time_start, 2), "predicted_rating_list" : predicted_rating, "original_rating_list" : original_rating}
    json.dumps(answer)
    print(answer)

def getpipedtags():
    objects = []

    tagged_dishes = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tagged_dishes.pickle"), "rb" ))

    for i in range(1, len(tagged_dishes)):
        tags = '|'.join(tagged_dishes[i][0])
        objects.append([i, tags])

    with open(os.path.join(my_path,"../Utilities/Team 3/database.csv"), 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(objects)

if __name__ == '__main__':
    getpipedtags()
    start()
