import argparse
from prettytable import PrettyTable
import pandas as pd
import os

import matF
import tfidf_flavour
import json
import clean_response
import health

my_path = os.path.abspath(os.path.dirname(__file__))

def print_tables(response, method):
	m = 'Matrix Factorisation' if method == 1 else 'Tf-Idf'

	t = PrettyTable(['USER', 'METHOD','RMSE'])
	t.add_row([response['user'], m, response['predicted_test_error']])
	print(t)

	print("\n")
	print("RECOMMENDED DISHES...")
	health_score = 'health_score' in response['predicted_rating'][0]
	if health_score:
		t = PrettyTable(['DISH NAME', 'PREDICTED RATING', 'HEALTH SCORE'])			
	else:
		t = PrettyTable(['DISH NAME', 'PREDICTED RATING'])

	for i in response['predicted_rating']:
		if health_score:
			t.add_row([i['dishName'], round(i['rating'], 2), i['health_score']])
		else:	
			t.add_row([i['dishName'], round(i['rating'], 2)])

	print(t)

	print("\n")
	print("DISHES REVIEWED BY USER...")
	t = PrettyTable(['DISH NAME', 'ORIGINAL RATING', 'PREDICTED RATING'])

	for i in response['original_rating']:
		t.add_row([i['dishName'], round(i['reformed'], 2), round(i['rating'], 2)])

	print(t)

ap = argparse.ArgumentParser()
# Arguments for Matrix Factorisation
ap.add_argument("--matF", action = 'store_true', help = "Matrix Factorisation Method")
ap.add_argument("--retrain", action = 'store_true', help = "Retrain For Matrix Factorisation")
# Arguments for Tf-Idf
ap.add_argument("--tfidf", action = 'store_true', help = "TF-IDF Method")
ap.add_argument("--type", help = "Pass 'all' for meta tags and cuisine tags or just 'meta' for meta tags")
ap.add_argument("--flavour", action = 'store_true', help = "if recommendation should include flavours")
# Arguments if health scores need to be included
ap.add_argument("--health", action = 'store_true', help = "Display health scores")
ap.add_argument("--steps", help = "Steps walked so far in the day")
ap.add_argument("--floors", help = "Steps climbed so far in the day")
# Arguments if user profile being passed on the fly
ap.add_argument("--profile", help = "Pass User Profile as JSON string to get recommendations for this user")
ap.add_argument("--nonveg", help = "Pass 1 if user non veg else 0")
# Predict on user, Alwaysneed to have this user in the user_profile database
ap.add_argument("--predict", help = "Pass User ID, To Make Predictions On")
# If output on terminal
ap.add_argument("--pretty", action = 'store_true', help = "Print Output on Terminal, Using Pretty Table")

argvalues = ap.parse_args()
# profile = '{"789": 5, "23": 5, "56": 2}'

if argvalues.profile:
	profile = argvalues.profile
else:
	profile = None

method = 0
if argvalues.matF:
	method = 1
	if argvalues.retrain:
		if argvalues.predict:
			response = matF.start(profile = profile, retrain = True, predict_on = int(argvalues.predict))
		else:
			response = matF.start(profile = profile, retrain  = True)

	else:
		if argvalues.predict:
			response = matF.start(profile = profile, retrain = False, predict_on = int(argvalues.predict))
		else:
			response = matF.start(profile = profile, retrain = False)

elif argvalues.tfidf:
	method = 2
	if argvalues.type:
		response = tfidf_flavour.start(profile = profile, type = argvalues.type, predict_on = int(argvalues.predict), flavours = argvalues.flavour)
	else:
		response = tfidf_flavour.start(profile = profile, predict_on = int(argvalues.predict), flavours = argvalues.flavour)

response['predicted_rating'].dropna(axis = 0, inplace = True)

predict_on_user = int(argvalues.predict) if argvalues.predict else 100

user_data = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/user_profile.csv'))
user_profile = user_data[user_data.userId == predict_on_user]

if argvalues.profile:
	if argvalues.nonveg:
		user_profile = pd.DataFrame({'userId' : [predict_on_user], 'nonveg' : [argvalues.nonveg]})

if argvalues.health:
	health_scores = health.main(user_profile, int(argvalues.steps), int(argvalues.floors), predict_on = int(argvalues.predict))
	health_scores = clean_response.scale_health_scores(health_scores)
else:
	health_scores = None

response['predicted_rating'] = clean_response.clean_dish_scores(response, health_scores, user_profile, predict_on = int(argvalues.predict))
response['original_rating'] = response['original_rating'].to_dict(orient = "records")

if argvalues.pretty:
	print_tables(response, method)

else:
	response = json.dumps(response)
	print(response)