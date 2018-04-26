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

		# sort by health score
		predicted_scores.sort_values(['health_score', 'rating'], ascending = [False, False], inplace = True)

	ans = predicted_scores.to_dict(orient = "records")
	answer = ans[:10]
	if include_bottom:
		answer.extend(ans[-5:])
	return answer

def scale_health_scores(scores):
	values = scores.values()
	min_value = min(values)
	max_value = max(values)
	new_values = {}

	for j in scores:
		i = scores[j]
		new_value = ((i - min_value) / (max_value - min_value)) * 100

		new_values[j] = new_value

	return new_values