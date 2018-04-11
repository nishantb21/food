import argparse
from prettytable import PrettyTable

import matF
import tfidf
import tfidf_flav
import json


def print_tables(response, method):
	m = 'Matrix Factorisation' if method == 1 else 'Tf-Idf'

	t = PrettyTable(['USER', 'METHOD','RMSE'])
	t.add_row([response['user'], m, response['predicted_test_error']])
	print(t)

	print("\n")
	print("RECOMMENDED DISHES...")
	t = PrettyTable(['DISH NAME', 'PREDICTED RATING'])
	for i in response['predicted_rating_list']:
		t.add_row([i['dish_name'], round(i['rating'], 2)])

	print(t)

	print("\n")
	print("DISHES REVIEWED BY USER...")
	t = PrettyTable(['DISH NAME', 'ORIGINAL RATING', 'PREDICTED RATING'])
	for i in response['original_rating_list']:
		t.add_row([i['dish_name'], i['original_rating'], round(i['predicted_rating'], 2)])

	print(t)


ap = argparse.ArgumentParser()
ap.add_argument("--matF", action = 'store_true', help = "Matrix Factorisation Method")
ap.add_argument("--tfidf", action = 'store_true', help = "TF-IDF Method")
ap.add_argument("--retrain", action = 'store_true', help = "Retrain For Matrix Factorisation")
ap.add_argument("--pretty", action = 'store_true', help = "Print Output on Terminal, Using Pretty Table")
ap.add_argument("--predict", help = "Pass User ID, To Make Predictions On")
ap.add_argument("--type", help = "Pass 'all' for meta tags and cuisine tags or just 'meta' for meta tags") # all and meta
ap.add_argument("--profile", help = "Pass User Profile as JSON string to get recommendations for this user")

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
		response = tfidf.start(profile = profile, type = argvalues.type, predict_on = int(argvalues.predict))
	else:
		response = tfidf.start(profile = profile, predict_on = int(argvalues.predict))

if argvalues.pretty:
	print_tables(response, method)

else:
	response = json.dumps(response)
	print(response)