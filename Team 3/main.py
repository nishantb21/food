import argparse
from prettytable import PrettyTable

import matF
import tfidf
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
ap.add_argument("--matF", action = 'store_true')
ap.add_argument("--tfidf", action = 'store_true')
ap.add_argument("--retrain", action = 'store_true')
ap.add_argument("--terminal", action = 'store_true')
ap.add_argument("--predict")
argvalues = ap.parse_args()

method = 0
if argvalues.matF:
	method = 1
	if argvalues.retrain:
		if argvalues.predict:
			response = matF.start(retrain = True, predict_on = int(argvalues.predict))
		else:
			response = matF.start(retrain  = True)

	else:
		if argvalues.predict:
			response = matF.start(retrain = False, predict_on = int(argvalues.predict))
		else:
			response = matF.start(retrain = False)

elif argvalues.tfidf:
	method = 2
	response = tfidf.start(predict_on = int(argvalues.predict))

if argvalues.terminal:
	print_tables(response, method)

else:
	response = json.dumps(response)
	print(response)