import pandas as pd
import json
import csv

import main

ratings = pd.read_csv('ratings.csv')

meta = pd.read_csv('meta.csv')

fh = csv.writer(open('final.csv', 'a+'))

for row in meta.iterrows():
	row = row [1]
	emailId = row['emailId']

	try:
		written = pd.read_csv('final.csv', names = ['emailId', 'dishId', 'dishName', 'rating', 'method'])
		if emailId in list(written.emailId):
			continue
	except:
		pass

	method = row['method']
	nonveg = row['nonveg']
	print(emailId)
	profile = ratings[ratings.emailId == emailId]
	profile = dict(zip(profile.dishId, profile.rating))
	profile = json.dumps(profile)

	predict = 22626

	health_bool = False
	steps = 0
	floors = 0

	pretty = False

	tfidf_type = None

	if method == 1:
		matf = True
		retrain = True

		tfidf = False
		flavour = False

	if method == 2:
		matf = False
		retrain = False
		
		tfidf = True
		flavour = False

	if method == 3:
		matf = False
		retrain = False
		
		tfidf = True
		flavour = True

	response = main.start(matf, retrain, tfidf, tfidf_type, flavour, health_bool, steps, floors, profile, nonveg, predict, pretty, include_bottom = True)

	final = []
	for i in response['predicted_rating']:
		final.append([emailId,i['dishId'],i['dishName'],i['rating'],method])

	fh.writerows(final)