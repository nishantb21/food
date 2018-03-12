import requests
import os
import json
import utilities
import sys
from multiprocessing import Pool

query_url = 'https://www.nutritionix.com/track-api/v2/search/instant?branded=true&common=true&self=false&query='
nutrition_url = 'https://www.nutritionix.com/nixapi/items/'
nutrition_common_url = 'https://www.nutritionix.com/track-api/v2/natural/nutrients'
brand_id_url = "https://d1gvlspmcma3iu.cloudfront.net/brands-restaurant.json.gz"
brand_dishes = 'https://www.nutritionix.com/nixapi/brands/{0}/items/1?limit=1000&search='


class NutritionixResponse:
	def __init__(self, item_type='common', name='name', item_id=None, nutrition_data=dict()):
		self.name = name
		self.item_id = item_id
		self.item_type = item_type
		self.nutrition_data = nutrition_data

	def __getitem__(self, key):
		try:
			return self.nutrition_data[key]
		except KeyError:
			return self.name


def save_for(brand):
	try:
		items_json = requests.get(brand_dishes.format(brand['id']))
		print(brand['name'] + ' | ', end='')
		items = items_json.json()
		print("Hits: ", items["total_hits"])
		count = 0
		for item in items["items"]:
			if not os.path.exists('branded_dishes/' + utilities.hash(item['item_name']) + ".json"):
				nutrition = requests.get(nutrition_url + item['item_id'])
				with open('branded_dishes/' + utilities.hash(item['item_name']) + ".json", 'w') as file:
					json.dump(utilities.standardize_keys(nutrition.json()), file, indent='\t')
					count += 1
		print("\r")
	except KeyError:
		pass


def leech_brand(brand_file):
	brand_ids = list()
	with open(brand_file) as brands:
		brand_ids = json.load(brands)
	with Pool(15) as ppool:
		ppool.map(save_for, brand_ids)


def ingredient(query):
	response = requests.get(query_url + utilities.parameterize(query))
	response_json = response.json()
	try:
		if response.status_code == 200:
			possible_matches = list()
			if len(response_json['common']) > 0:
				for rid in range(min(3, len(response_json['common']))):
					possible_matches.append(NutritionixResponse(item_type='common', name=response_json['common'][rid]['food_name'], item_id=None))
			elif len(response_json['branded']) > 0:
				for rid in range(min(3, len(response_json['branded']))):
					possible_matches.append(NutritionixResponse(item_type='branded', name=response_json['branded'][rid]['brand_name_item_name'], item_id=response_json['branded'][rid]['nix_item_id']))
			best_match = utilities.modmatchir(query, possible_matches, 0.2)
			if best_match is not None:
				if best_match.item_type == 'common':
					response_nutrition = requests.post(nutrition_common_url, data={"query": best_match.name})
					response_nutrition = response_nutrition.json()
					try:
						response_nutrition = response_nutrition['foods'][0]
					except json.decoder.DecodeError:
						pass
					return NutritionixResponse(name=response_nutrition['food_name'], item_type='common', nutrition_data=utilities.standardize_keys(response_nutrition))

				response_nutrition = requests.get(nutrition_url + best_match.item_id)
				response_nutrition = response_nutrition.json()
				return NutritionixResponse(name=best_match.name, item_type='branded', item_id=best_match.item_id, nutrition_data=response_nutrition)
		else:
			return None
	except KeyError:
		pass


def leech(for_file, folder):
	with open(for_file) as queries, open('misses_' + queries.name.split("/")[-1], 'w') as misses:

		for query in queries:
			returned_item = ingredient(query.strip())
			title_hash = utilities.hash(query)
			if returned_item is not None:
				if not os.path.exists(folder):
					os.makedirs(folder)
				if not os.path.exists(os.path.join(folder, title_hash + ".json")):
					with open(os.path.join(folder, title_hash + ".json"), "w") as ing_file:
						json.dump(returned_item.nutrition_data, ing_file, indent='\t')
			else:
				misses.write(query)


def assign(values):
	leech(values, sys.argv[2])


if __name__ == '__main__':
	'''
	with Pool(8) as ppool:
		ppool.map(assign, glob.iglob(sys.argv[1] + "/food_names.*"))
	'''
	save_for(
		{
			"id": "569010fe25bbe91d1fc2b671",
			"name": "tendergreens"
		}
	)
