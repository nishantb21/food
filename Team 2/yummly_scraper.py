"""
This module queries yummly.com for dish details and stores it in a JSON file
"""
import sys
import json
import pickle
import requests
from collections import OrderedDict 

app_id = '<api_id_yummly>'
api_key = '<api_key_yummly>'





def get_data(food):
	"""
    Sends a request to yummly with the dish name parameter in the 
    search string
    """
	food = '+'.join(food.split(' '))
	#query = 'q='+food
	url = 'https://mapi.yummly.com/mapi/v16/content/search?q=' + food + '&start=0&maxResult=36&fetchUserCollections=false&allowedContent[]=single_recipe&allowedContent[]=suggested_source&allowedContent[]=suggested_search&allowedContent[]=related_search&allowedContent[]=article&allowedContent[]=video&facetField[]=diet&facetField[]=holiday&facetField[]=technique&facetField[]=cuisine&facetField[]=course&facetField[]=source&facetField[]=brand&facetField[]=difficulty&facetField[]=dish&facetField[]=adtag&guided-search=true&solr.view_type=search_internal'
	result = requests.get(url)
	#print(result)
	if result.text:
		return json.loads(result.text)
	else:
		print(food)

def open_item_details(item_details):
	"""
    Loads the item_details file, that consists of the database.
    """
	with open(item_details) as f:
		data = json.load(f, object_pairs_hook=OrderedDict)
	return data

def write_json_to_file(file):
	"""
    Writes the data to a JSON file
    """
	with open(file,'w+') as f:
		json.dump(item_details,f)

item_details = open_item_details('itemdetails.json')

def align_json_to_schema(res):
	"""
    The response from a Yummly query must be realigned to a schema that
    fits our use case.
    
    Keyword arguments:
    res          --  Response JSON object from the Yummly query
	
	Returns:
	item_dict  --  a dictionary that contains the details of the dish
				   in the required schema
    """
	item_dict = dict()
	global dish_id
	item_dict["dish_id"] = dish_id
	dish_id += 1
	item_dict["dish_name"] = res['display']['displayName']
	item_dict["description"] = res['content']['description']
	item_dict["overall_rating"] = res['content']['details']['rating']
	item_dict['image_url'] = res['content']['details']['images'][0]['resizableImageUrl']
	item_dict["url"] = res['content']['details']['attribution']['url']
	ingredients = res['content']['ingredientLines']
	ingredients = [i['wholeLine'] for i in ingredients]
	item_dict['ingredients'] = ingredients
	item_dict['directions'] = list()
	item_dict['prep_time'] = 0
	item_dict['cook_time'] = res['content']['details']['totalTimeInSeconds']
	item_dict['total_time'] = item_dict['cook_time']
	item_dict['nutrients'] = dict()
	nutrition = res['content']['nutrition']['nutritionEstimates']
	item_dict['nutrients']['Calories'] = str(-1) + ' kcal'
	item_dict['nutrients']['Fat'] = str(-1) + ' g'
	item_dict['nutrients']['Carbs'] = str(-1) + ' g'
	item_dict['nutrients']['Protein'] = str(-1) + ' g'
	item_dict['nutrients']['Cholesterol'] = str(-1) + ' mg'
	item_dict['nutrients']['Sodium'] =  str(-1) + ' mg'
	# Refer to https://developer.yummly.com/documentation for 
	# nutrient codes
	for nutrient in nutrition:
		if nutrient['attribute'] == 'FAT':
			item_dict['nutrients']['Fat'] = [str(nutrient['value']) + ' g',str(nutrient['display']['percentDailyValue']) + '%']
		elif  nutrient['attribute'] == 'CHOCDF':
			item_dict['nutrients']['Carbs'] = [str(nutrient['value']) + 'g',str(nutrient['display']['percentDailyValue']) + '%']
		elif  nutrient['attribute'] == 'PROCNT':
			item_dict['nutrients']['Protein'] = [str(nutrient['value']) + ' g',str(nutrient['display']['percentDailyValue']) + '%']
		elif  nutrient['attribute'] == 'CHOLE':
			item_dict['nutrients']['Cholesterol'] = [str(nutrient['value'])+ ' mg',str(nutrient['display']['percentDailyValue']) + '%']
		elif  nutrient['attribute'] == 'ENERC_KCAL':
			item_dict['nutrients']['Calories'] = [str(nutrient['value']) + ' kcal',str(nutrient['display']['percentDailyValue']) + '%']
		elif  nutrient['attribute'] == 'NA':
			item_dict['nutrients']['Sodium'] = [str(nutrient['value'])+ ' mg',str(nutrient['display']['percentDailyValue']) + '%']
	return item_dict

dish_id = 1

if __name__ == '__main__':
	if len(sys.argv) == 2:
		foods = [i.strip() for i in open(sys.argv[1]).readlines()]
		list_used = foods
		for food in list_used:
			res = get_data(food)
			if res:
				print("Retrieved",food)
				for i in res['feed'][:3]:
					i_dict = align_json_to_schema(i)
					item_details.append(i_dict)
			else:
				print("Couldn't find",food)

		with open('dict.pickle','wb') as p:
			pickle.dump(item_details,p)
		write_json_to_file('itemdetails.json')
	else:
		print("USAGE: python3 yummly_scraper.py <path_to_dishes_list>")


	