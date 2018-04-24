from collections import defaultdict
import json
import os

my_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(my_path,'../Utilities/Database/database.json'), 'r') as json_data:
	d = json.load(json_data)
	d = list(d)
	seafood = ['fish', 'crab', 'prawn']
	gluten = ['samosa', 'spring roll', 'naan', 'jalebi', 'pizza', 'bun', 'bhel', 'puri', 'upma', 'wheat', 'barley', 'starch', 'pasta', 'noodle', 'pancake', 'waffle', 'roti', 'paratha', 'poori', 'sooji', 'suji', 'rava']
	allergens = ['egg', 'peanut', 'soybean', 'cashew', 'nuts', 'soy']
	dairy = ['milk', 'paneer', 'curd']
	allergendict = defaultdict(list)
	for item in gluten:
		for dish in d:
			if (item in str(dish['ingredients']) or item in str(dish['dish_name'])):
				allergendict['gluten'].append(dish['dish_id'])
	for item in seafood:
		for dish in d:
			if (item in str(dish['ingredients']) or item in str(dish['dish_name'])):
				allergendict['seafood'].append(dish['dish_id'])
	for item in dairy:
		for dish in d:
			if (item in str(dish['ingredients']) or item in str(dish['dish_name'])):
				allergendict['dairy'].append(dish['dish_id'])
	for allergen in allergens:
		for dish in d:
			if (allergen in str(dish['ingredients']) or item in str(dish['dish_name'])):
				allergendict[allergen].append(dish['dish_id'])

with open(os.path.join(my_path,'../Utilities/Team 3/allergens.json'), 'w+') as jfile:
	json.dump(allergendict,jfile)