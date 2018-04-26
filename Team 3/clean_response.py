import json
import pandas as pd
import pickle
import os

my_path = os.path.abspath(os.path.dirname(__file__))

def clean_dish_scores(response, health_scores, user_profile, include_bottom, predict_on = 100):
	predicted_scores = response['predicted_rating']
	original_scores = response['original_rating']

	predicted_scores = predicted_scores[~predicted_scores.dishId.isin(original_scores.dishId)]

	nonveg = int(user_profile['nonveg'].iloc[0])

	if not nonveg:
		tagged_dishes = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tagged_dishes.pickle"), "rb" ))
		
		keys = tagged_dishes.keys()
		values = list(tagged_dishes.values())

		values = [i[1] for i in values]

		veg_non_veg_df = pd.DataFrame(columns = ['dishId', 'nonveg'])
		veg_non_veg_df.dishId = keys
		veg_non_veg_df.nonveg = values

		veg_non_veg_df = veg_non_veg_df[veg_non_veg_df.nonveg == 1]

		predicted_scores = predicted_scores[~predicted_scores.dishId.isin(veg_non_veg_df.dishId)]

	allergies = json.load(open(os.path.join(my_path,'../Utilities/Team 3/allergens.json'), 'rb'))
	allergens = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/user_allergies.csv'))
	allergens = allergens[allergens.userId == predict_on]
	
	list_allergy_dishes = []
	if allergens.shape[0] > 0:
		for i in allergens.allergy:
			list_allergy_dishes.extend(allergies[i])

		predicted_scores = predicted_scores[~predicted_scores.dishId.isin(list_allergy_dishes)]

	if health_scores:
		keys = health_scores.keys()
		values = health_scores.values()

		health_df = pd.DataFrame(columns = ['dishId', 'health_score'])
		health_df['dishId'] = keys
		health_df['health_score'] = values

		predicted_scores = predicted_scores.merge(health_df, how = 'left', on = 'dishId')

		predicted_scores = predicted_scores[predicted_scores.health_score > 1]
		predicted_scores.health_score = scale(predicted_scores.health_score)

		predicted_scores['final_score'] = 0.7 * predicted_scores.rating + 0.3 * predicted_scores.health_score

	else:
		predicted_scores['final_score'] = predicted_scores.rating

	ans = predicted_scores.to_dict(orient = "records")

	answer = [ans[0]]
	dishes = [ans[0]['dishName']]

	i = 0
	while len(answer) <= 10:
		i += 1
		if ans[i]['dishName'] not in dishes:
			answer.append(ans[i])
			dishes.append(ans[i]['dishName'])

	if include_bottom:
		answer.extend(ans[-5:])

	answer = sorted(answer, key = lambda x: x['final_score'], reverse = True)

	return answer

def scale(scores):
	old_max = max(scores)
	final = []

	for i in scores:
		final.append((i / old_max) * 5)

	return final