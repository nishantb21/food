import pandas as pd
from collections import Counter
import tensorflow as tf
from tffm import TFFMRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
import pickle
from sklearn.feature_extraction import DictVectorizer
import time
import json
import tag
import os

my_path = os.path.abspath(os.path.dirname(__file__))

def process_for_prediction(df, dishes, final_dict, all_tag_dict, unique_tags, user_id):
	tag_list = []
	for i in dishes.dishName:
		tags = tag.get_tags_as_dict(final_dict, i)
		if tags:
			tag_list.append(tags)
		else:
			tag_list.append(all_tag_dict)

	v = DictVectorizer(sparse = False)
	matrix = v.fit_transform(tag_list)
	dish_scores = pd.DataFrame(matrix)
	user_profile = df[df.userId == user_id].iloc[[0]][list(range(unique_tags, 2 * unique_tags))]
	user_profile = pd.concat([user_profile] * dish_scores.shape[0], ignore_index = True)
	dish_scores = pd.concat([dish_scores, user_profile], axis = 1)
	data_to_predict = np.array(dish_scores)

	return data_to_predict

def start(predict_on = 100):
	dishes = pd.read_csv(os.path.join(my_path,'../Utilities/Team 2/id_name_mapping.csv'), names = ['dishId', 'dishName'])
	df = pd.read_csv(os.path.join(my_path,'../Utilities/Team 2/review.csv'))
	df = df[df['userId'].isin(df['userId'].value_counts()[df['userId'].value_counts()>=5].index)]
	
	time_start = time.time()

	df = df.merge(dishes, on = 'dishId', how = 'left')

	all_tag_list = tag.all_unique_tags()
	all_tag_dict = {i : 0 for i in all_tag_list}

	final_dict = pickle.load(open(os.path.join(my_path,"../Utilities/Team 2/tagged_dishes.pickle"), 'rb'))
	df['tagged'] = 1

	tag_list = []
	for line in df.iterrows():
		d = line[1]
		tags = tag.get_tags_as_dict(final_dict, d['dishName'])
		if tags:
			tags = tag.get_difference(all_tag_dict, tags) # had {tag : 1, ...} if tag was present adding {tag : 0} if tag not present 
			tag_list.append(tags)
		else:
			df.at[line[0], 'tagged'] = 0

	df = df[df.tagged != 0]

	
	v = DictVectorizer(sparse = False)
	matrix = v.fit_transform(tag_list)
	unique_tags = matrix.shape[1]
	dish_scores = pd.DataFrame(matrix)

	
	df.reset_index(drop = True, inplace = True)
	dish_scores.reset_index(drop = True, inplace = True)

	df = pd.concat([df, dish_scores], axis = 1)

	user_profile = df.drop(['dishId', 'rating', 'tagged', 'dishName'], axis = 1)
	user_profile = user_profile.groupby(user_profile.userId).agg('sum')

	user_profile.columns = np.array(user_profile.columns) + unique_tags
	user_profile['userId'] = user_profile.index

	df = df.merge(user_profile, on = 'userId', how = 'left')

	model = TFFMRegressor(
		order=1,
		rank=1,
		optimizer=tf.train.AdamOptimizer(learning_rate=0.1),
		n_epochs=1000,
		batch_size=-1,
		init_std=0.001,
		input_type='dense'
	)
	
	X = df[['dishId', 'userId'] + list(range(0, df.shape[1] - 5))]
	y = df.rating
	X = np.array(X)
	X = np.nan_to_num(X)
	y = np.nan_to_num(y)

	X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1, random_state = 42)

	model.fit(X_tr[:,2:], y_tr, show_progress = False)

	predictions = model.predict(X_te[:,2:])
	predicted_test_error = mean_squared_error(y_te, predictions) ** 0.5

	time_end = time.time()

	data_to_predict = process_for_prediction(df, dishes, final_dict, all_tag_dict, unique_tags, predict_on)
	predictions = model.predict(data_to_predict)
	
	dishes_scored = df[df.userId == predict_on]

	predicted_rating_original = []
	for i in dishes_scored.iterrows():
		predicted_rating_temp = {}
		d = i[1]
		predicted_rating_temp["dish_name"] = d["dishName"]
		predicted_rating_temp["original_rating"] = d["rating"]
		predicted_rating_temp["predicted_rating"] = round(float(predictions[d["dishId"] - 1]), 2)
		predicted_rating_original.append(predicted_rating_temp)

	
	predictions = list(enumerate(predictions))
	predictions = sorted(predictions, key = lambda x:x[1], reverse = True)

	predicted_rating_list = []
	predictions = predictions[:10]
	for i in predictions:
		predicted_rating = {}
		predicted_rating["dish_name"] = dishes[dishes.dishId == i[0]].dishName.values[0]
		predicted_rating["rating"] = round(float(i[1]), 2)
		predicted_rating_list.append(predicted_rating)

	answer = {"user" : predict_on, 'time' : time_end - time_start,  'predicted_test_error' : predicted_test_error, 'original_rating_list': predicted_rating_original, 'predicted_rating_list' : predicted_rating_list}
	answer = json.dumps(answer)
	print(answer)

	model.destroy()