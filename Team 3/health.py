import geocoder
import pyowm
import json
import requests
import pandas as pd
import os
my_path = os.path.abspath(os.path.dirname(__file__))

def get_lat_long(ip_addr = 'me'):
	g = geocoder.ip(ip_addr)
	return g.latlng

def get_temp(lat, lon):
	owm = pyowm.OWM('9bb248641cc71b7ab1b7040317ec6ac9')
	observation_list = owm.weather_around_coords(lat, lon)
	tot_temp = 0
	if observation_list != None:
		for i in observation_list:
			w = i.get_weather()
			temp = w.get_temperature('fahrenheit')['temp']
			tot_temp += temp

		temp = tot_temp / len(observation_list)

		return temp

def elevation(lat, lng):
	loc = str(lat) + ',' + str(lng)
	apikey = "AIzaSyDiBZHG5Oq-NQeMkjTqPldFmAV1k-nuu1c"
	base_url = "https://maps.googleapis.com/maps/api/elevation/json"
	params = dict()
	params["locations"] = str(loc)
	params["key"] = apikey
	r = requests.get(base_url, params=params)
	results = json.loads(r.text).get('results')

	return results[0]['elevation']

def adaptive_daily_value(weight, height, gender, age, steps, height_travelled, bmratio):
	latlong = get_lat_long()
	
	temp = get_temp(*latlong)
	altitude = elevation(*latlong)

	allowed = {'calories' : 2079.35, 'protein' : 50, 'fat' : 70, 'sat_fat' : 24, 'carbs' : 310, 'sugar' : 30, 'dietary_fiber' : 30, 'sodium' : 2.3, 'cholesterol' : 300, 'vitamin_a' : 0.0008, 'vitamin_c' : 0.08, 'iron' : 0.0087, 'calcium' : 1}
	
	work = 9.8 * weight * height_travelled * 0.000239006 + weight * steps / 6000

	bmr = weight * 10 + 6.25 * height - 5 * age
	if gender == 'm':
		bmr += 5
	else:
		bmr -= 161

	daily_cal = round(bmratio * bmr + work, 2)

	if temp != None:
		daily_cal = daily_cal * (1 + (85 - temp) / 8000)

		for i in allowed:
			allowed[i] = allowed[i] * daily_cal / 2079.35

	na_multi = 1 + 0.015 * (((temp - 32) * 0.56) - 23)
	allowed['sodium'] = na_multi * allowed['sodium'] + (altitude / 1000) ** 2.5
	
	return allowed


def elixir(allowed, weights, type = 'normal'):
	weights = weights[type]
	database = json.load(open(os.path.join(my_path,"../Utilities/Database/database.json")))
	x = {}
	for dish in database:
		dishId = dish['dish_id']
		nutrients = dish['nutrients']
		if all(nutrients.values()):
			for nutrient in nutrients:
				value = nutrients[nutrient]
				if value:
					value = value[0]
					if value.endswith('mg'):
						value = value[:value.index('mg')]
						value = value.replace(",", "")
						value = value.replace(" ", "")
						value = float(value) / 1000
					elif value.endswith('g'):
						value = value[:value.index('g')]
						value = value.replace(",", "")
						value = value.replace(" ", "")
						value = float(value)
					elif value.endswith('kcal'):
						value = value[:value.index('kcal')]
						value = value.replace(",", "")
						value = value.replace(" ", "")
						value = float(value)

					elif value.endswith('IU'):
						value = value[:value.index('IU')]
						value = value.replace(",", "")
						value = value.replace(" ", "")
						value = (float(value) / 3.3) / 1000000

					nutrients[nutrient] = value
			#################################
			recbn = ['protein', 'dietary_fiber']
			recbase = 0
			for i in recbn:
				recbase += weights[i] * nutrients[i] / allowed[i]

			part1 = 0
			part2 = 0
			if nutrients['carbs']:
				part1 = weights['dietary_fiber'] * nutrients['dietary_fiber'] / nutrients['carbs']
				part2 =  0.1 * (nutrients['carbs'] - nutrients['dietary_fiber'] - nutrients['sugar']) / nutrients['carbs']

			recbase = recbase + part1 + part2
			#################################
			restbn = ['carbs', 'cholesterol', 'sodium', 'sat_fat', 'fat', 'sugar']
			restbase = 0
			for i in restbn:
				restbase += weights[i] * nutrients[i] / allowed[i]

			part1 = 0
			part2 = 0
			if nutrients['sugar'] and nutrients['carbs']:
				part1 = weights['carbs'] * nutrients['sugar'] / nutrients['carbs']

			if nutrients['sat_fat'] and nutrients['fat']:
				part2 = weights['sat_fat'] * nutrients['sat_fat'] / nutrients['fat']
			
			restbase = part1 + part2			
			#################################
			recan = ['vitamin_a', 'vitamin_c', 'calcium', 'iron']
			recadd = 0
			for i in recan:
				recadd += weights[i] * nutrients[i] / allowed[i]
			#################################

			mult = 10
			div = ((1 + mult) * restbase)
			if div:
				score = recbase + (mult * recadd) / div
			else:
				score = 0

			x[dishId] = score

	return x

weights = {
	'normal' : {'calories' : 1, 'protein' : 1, 'sugar' : 1.1, 'fat' : 1.1, 'sat_fat': 1.7, 'carbs' : 1, 'dietary_fiber' : 1.5, 'sodium' : 1, 'cholesterol' : 1.2, 'vitamin_a' : 1, 'vitamin_c' : 1, 'calcium' : 1, 'iron' : 1}, 
	'diabetes' : {'calories' : 1, 'protein' : 1, 'sugar' : 4.25, 'fat' : 1.1, 'sat_fat': 1.7, 'carbs' : 1, 'dietary_fiber' : 3, 'sodium' : 1, 'cholesterol' : 1.2, 'vitamin_a' : 1, 'vitamin_c' : 1, 'calcium' : 1, 'iron' : 1},
	'bp' : {'calories' : 1, 'protein' : 1, 'sugar' : 1.1, 'fat' : 1.1, 'sat_fat': 1.7, 'carbs' : 1, 'dietary_fiber' : 1.5, 'sodium' : 9, 'cholesterol' : 1.2, 'vitamin_a' : 1, 'vitamin_c' : 1, 'calcium' : 1, 'iron' : 1},
	'obesity' : {'calories' : 7, 'protein' : 1, 'sugar' : 1.1, 'fat' : 1.1, 'sat_fat': 1.7, 'carbs' : 1, 'dietary_fiber' : 1.5, 'sodium' : 1, 'cholesterol' : 1.2, 'vitamin_a' : 1, 'vitamin_c' : 1, 'calcium' : 1, 'iron' : 1}
	}

def main(user_profile, steps, floors, predict_on = 100):
	height = float(user_profile['height'][0])
	weight = float(user_profile['weight'][0])
	age = float(user_profile['age'][0])
	gender = user_profile['gender'][0]
	condition = user_profile['condition'][0]
	bmratio = float(user_profile['bmratio'][0])

	floors = floors * 10 * 3.28084

	allowed = adaptive_daily_value(weight, height, gender, age, steps, floors, bmratio)
	score = elixir(allowed, weights, type = condition)
	
	return score