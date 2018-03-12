import numpy as np
import pandas as pd
import pickle
import json
import math
import time
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import os

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
		    '''
		    if (i+1) % 5 == 0:
		        print("Iteration: %d ; error = %.4f" % (i+1, mse))
		    '''

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
		return self.b + self.b_u[:,np.newaxis] + self.b_i[np.newaxis:,] + self.P.dot(self.Q.T)


def predict(final_scores, dishes, userId):
	rowUser = final_scores[userId, :]
	rowSort = sorted(np.ndenumerate(rowUser), key = lambda x: x[1], reverse = True)
	predictions = [(i[0][0], i[1]) for i in rowSort[:10]]
	predictions = pd.DataFrame(predictions, columns = ['dishId', 'rating'])
	predictions = predictions.merge(dishes, on = 'dishId', how = 'left')
	return predictions

def original(final_scores, dishes, df, userId):
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


def start(retrain = False, predict_on = 100):
	dishes = pd.read_csv(os.path.join(my_path,'../Utilities/Team 2/id_name_mapping.csv'), names = ['dishId', 'dishName'])
	df = pd.read_csv(os.path.join(my_path,'../Utilities/Team 2/review.csv'))
	df = df[df['userId'].isin(df['userId'].value_counts()[df['userId'].value_counts()>=5].index)]

	n_users = df.userId.unique().max()
	n_dishes = df.dishId.unique().max()

	df, test_set = train_test_split(df, test_size = 0.20, random_state = 42)

	time_start = time.time()

	if retrain:
		data = np.zeros((n_users + 1, n_dishes + 1))

		for line in df.iterrows():
			d = line[1]
			
			dish_id = d["dishId"]
			user_id = d["userId"]
			rating  = d["rating"]

			data[user_id, dish_id] = rating


		mf = MF(data, K = 64, alpha = 0.1, beta = 0.01, iterations = 100)

		training_process = mf.train()
		final_scores = mf.full_matrix()
		pickle.dump(final_scores, open(os.path.join(my_path,'../Utilities/Team 2/final_scores.pickle'), 'wb'))

	else:
		final_scores = pickle.load(open(os.path.join(my_path,"../Utilities/Team 2/final_scores.pickle"), "rb" ))

	time_end = time.time()

	predicted_rating = predict(final_scores, dishes, predict_on)
	original_rating = original(final_scores, dishes, df, predict_on)

	predicted_rating = df_to_list(predicted_rating, ['dishName', 'rating'])
	original_rating = df_to_list(original_rating, ['dishName', 'rating', 'reformed'])
	predicted_final = []
	original_final = []

	for i in predicted_rating:
		predicted_final_temp = {}
		predicted_final_temp['dish_name'] = i[0]
		predicted_final_temp['rating'] = round(i[1], 2)
		predicted_final.append(predicted_final_temp)

	for i in original_rating:
		original_rating_temp = {}
		original_rating_temp['dish_name'] = i[0]
		original_rating_temp['original_rating'] = round(i[1], 4)
		original_rating_temp['predicted_rating'] = round(i[2], 4)
		original_final.append(original_rating_temp)

	test_data = np.zeros((n_users + 1, n_dishes + 1))
	for line in test_set.iterrows():
			d = line[1]

			dish_id = d["dishId"]
			user_id = d["userId"]
			rating  = d["rating"]

			test_data[user_id, dish_id] = rating

	predicted_test_error = mean_squared_error(test_data[test_data.nonzero()].flatten(), final_scores[test_data.nonzero()].flatten()) ** 0.5

	answer = {'predicted_rating_list': predicted_final, 'original_rating_list': original_final, "user" : predict_on, 'time' : time_end - time_start, 'predicted_test_error' : predicted_test_error}
	if retrain:
		answer['sum_square_error'] = training_process[-1][1]
	else:
		answer['sum_square_error'] = None

	answer = json.dumps(answer)

	print(answer)