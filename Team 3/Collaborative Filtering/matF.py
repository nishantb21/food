import numpy as np
import pandas as pd
import pickle
import json
import math
import time
import argparse
import os
from sklearn.metrics import mean_squared_error
my_path = os.path.abspath(os.path.dirname(__file__))
class MF():

    def __init__(self, R, K, alpha, beta, iterations):
        """
        Perform matrix factorization to predict empty
        entries in a matrix.

        Arguments
        - R (ndarray)   : user-item rating matrix
        - K (int)       : number of latent dimensions
        - alpha (float) : learning rate
        - beta (float)  : regularization parameter
        """

        self.R = R
        self.num_users, self.num_items = R.shape
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations

    def train(self):
        # Initialize user and item latent feature matrice
        np.random.seed(42)
        self.P = np.random.normal(scale=1./self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1./self.K, size=(self.num_items, self.K))

        # Initialize the biases
        self.b_u = np.zeros(self.num_users)
        self.b_i = np.zeros(self.num_items)
        self.b = np.mean(self.R[np.where(self.R != 0)])

        # Create a list of training samples
        '''
        self.samples = [
            (i, j, self.R[i, j])
            for i in range(self.num_users)
            for j in range(self.num_items)
            if self.R[i, j] > 0
        ]
        '''

        self.non_z = self.R.nonzero()
        self.samples = list(zip(self.non_z[0], self.non_z[1], self.R[self.non_z]))

        # Perform stochastic gradient descent for number of iterations
        training_process = []
        for i in range(self.iterations):
            np.random.shuffle(self.samples)
            self.sgd()
            mse = self.mse()
            training_process.append((i, mse))
            # if (i+1) % 10 == 0:
            #     print("Iteration: %d ; error = %.4f" % (i+1, mse))

        return training_process

    def mse(self):
        """
        A function to compute the total mean square error
        """

        '''
        xs, ys = self.R.nonzero()
        predicted = self.full_matrix()
        error = 0
        for j in zip(xs, ys):
            error += pow(self.R[j] - predicted[j], 2)
            # print(self.R[j], predicted[j])
        # print("ERROR ", error, np.sqrt(error))
        return np.sqrt(error)
        '''

        predicted = self.full_matrix()
        real_values = self.R[self.non_z].flatten()
        predicted_values = predicted[self.non_z].flatten()
        return np.sum((real_values - predicted_values) ** 2) ** 0.5


    def sgd(self):
        """
        Perform stochastic graident descent
        """
        for i, j, r in self.samples:
            # Computer prediction and error
            prediction = self.get_rating(i, j)
            e = (r - prediction)

            # Update biases
            self.b_u[i] += self.alpha * (e - self.beta * self.b_u[i])
            self.b_i[j] += self.alpha * (e - self.beta * self.b_i[j])

            # Update user and item latent feature matrices
            self.P[i, :] += self.alpha * (e * self.Q[j, :] - self.beta * self.P[i,:])
            self.Q[j, :] += self.alpha * (e * self.P[i, :] - self.beta * self.Q[j,:])

    def get_rating(self, i, j):
        """
        Get the predicted rating of user i and item j
        """

        prediction = self.b + self.b_u[i] + self.b_i[j] + self.P[i, :].dot(self.Q[j, :].T)
        return prediction

    def full_matrix(self):
        """
        Computer the full matrix using the resultant biases, P and Q
        """
        return mf.b + mf.b_u[:,np.newaxis] + mf.b_i[np.newaxis:,] + mf.P.dot(mf.Q.T)


def predict(userId):
    rowUser = final_scores[userId, :]
    rowSort = sorted(np.ndenumerate(rowUser), key = lambda x: x[1], reverse = True)
    predictions = [(i[0][0], i[1]) for i in rowSort[:10]]
    predictions = pd.DataFrame(predictions, columns = ['dishId', 'rating'])
    predictions = predictions.merge(dishes, on = 'dishId', how = 'left')
    return predictions

def original(userId):
    actualRatings = df[df.userId == userId]
    totalActualRating = len(actualRatings)
    rowUser = final_scores[userId, :]
    originalReformed = [rowUser[i] for i in actualRatings.dishId]
    actualRatings = actualRatings.merge(dishes, on = 'dishId', how = 'left')
    actualRatings['reformed'] = originalReformed
    return actualRatings


def df_to_list(dataframe, columns):
    dataframe = dataframe[columns]
    result = dataframe.values.tolist()
    return result


ap = argparse.ArgumentParser()
ap.add_argument("--predict")
argvalues = ap.parse_args()

# predictOn = 100 # default prediction on

if argvalues.predict:
    predictOn = int(argvalues.predict)

dishes = pd.read_csv(os.path.join(my_path,'../../Utilities/Team 2/idNameMapping.csv'), names = ['dishId', 'dishName'])
df = pd.read_csv(os.path.join(my_path,'../../Utilities/Team 2/review.csv'))
df = df[df['userId'].isin(df['userId'].value_counts()[df['userId'].value_counts()>=5].index)]

# print(df.tail())
# print(predictOn)
# print(df.tail().userId)

# print()

if len(df[df.userId == predictOn]) > 0:
    # read pickle and set final scores
    final_scores = pickle.load(open(os.path.join(my_path,"../../Utilities/Team 2/finalScores.pickle"), "rb" ))

else:
    n_users = df.userId.unique().max()
    n_dishes = df.dishId.unique().max()

    data = np.zeros((n_users + 1, n_dishes + 1))

    for line in df.iterrows():
        d = line[1]

        dish_id = d["dishId"]
        user_id = d["userId"]
        rating  = d["rating"]

        data[user_id, dish_id] = rating


    mf = MF(data, K = 64, alpha = 0.1, beta = 0.01, iterations = 100)

    time_start = time.time()

    training_process = mf.train()
    final_scores = mf.full_matrix()
    pickle.dump(final_scores, open(os.path.join(my_path,'../../Utilities/Team 2/finalScores.pickle'), 'wb'))

time_end = time.time()

predicted_rating = predict(predictOn)
original_rating = original(predictOn)

predicted_rating = df_to_list(predicted_rating, ['dishName', 'rating'])
original_rating = df_to_list(original_rating, ['dishName', 'rating', 'reformed'])

predicted_final = []
original_final = []

for i in predicted_rating:
    predicted_final_temp = {}
    predicted_final_temp['dish_name'] = i[0]
    predicted_final_temp['rating'] = round(i[1],2)
    predicted_final.append(predicted_final_temp)

for i in original_rating:
    original_rating_temp = {}
    original_rating_temp['dish_name'] = i[0]
    original_rating_temp['original_rating'] = i[1]
    original_rating_temp['predicted_rating'] = i[2]
    original_final.append(original_rating_temp)

answer = {'predicted_rating_list': predicted_final, 'original_rating_list': original_final, "user" : predictOn} # 'error' : training_process[-1][1], 'time' : time_end - time_start
answer = json.dumps(answer)

print(answer)
# print(time_end - time_start)
