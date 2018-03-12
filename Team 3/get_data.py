from urllib.request import urlopen
from bs4 import BeautifulSoup
import pickle
import csv
from collections import OrderedDict
import json
import time

def get_dish_name():
	"""
	Get all dish names along with their description, rating out of 5, link to image, link to recipe page from website www.allrecipes.com

	Input - None (URL hardcoded)
	Output - dishnames.csv

	Output of the form -
	dishId, dishName, description, overallRating, imageURL, recipe URL

	1,Curried Green Bean Salad,"This version of a cold bean salad is made with canned green beans, garlic, ginger, and curry powder.",3.75,http://images.media-allrecipes.com/userphotos/250x250/01/04/27/1042750.jpg,allrecipes.com/recipe/222038/curried-green-bean-salad/
	"""

	urlList = []

	url_ = "http://allrecipes.com/recipes/233/world-cuisine/asian/indian/?page="

	recipeId = 1
	# 1 - 37 for indian dishes
	for i in range(1, 38):
		url = url_ + str(i)
		page = urlopen(url)
		soup = BeautifulSoup(page, "lxml")
		print("-------------------" + str(i) + "-------------------")

		htmlUrls = soup.find_all('article', {'class': "fixed-recipe-card"})

		for html in htmlUrls:
			imageTag = html.find('img', {'class', 'fixed-recipe-card__img'})
			if imageTag != None:
				imageLink = imageTag.attrs['data-original-src']
			else:
				imageLink = ""

			info = html.find('div', {'class', 'fixed-recipe-card__info'})
			if info != None:
				link_name = info.find('a', {'class', 'fixed-recipe-card__title-link'})
				link = 'allrecipes.com' + link_name.attrs['href']
				name = link_name.text.strip()
				des = info.find('div', {'class', 'fixed-recipe-card__description'})
				if des != None:
					des = des.text.strip()
				else:
					des = ""
				rating = info.find('span', {'class', 'stars'}).attrs['data-ratingstars']

				print([recipeId, name, des, rating, imageLink, link])
				urlList.append([recipeId, name, des, rating, imageLink, link])
				recipeId += 1

	with open("dishnames.csv", "w+") as f:
	    writer = csv.writer(f)
	    writer.writerows(urlList)



def get_dish_details():
	"""
	Scrape all all details pertaining to dish form the allrecipes website

	Input - dishnames.csv
	Output - itemdetails.json

	Output contains - 
	dishId, dishName, description, overallRating, imageURL, URL, ingredients, directions, prep time, cook time, total time, nutrients

	NOTE : itemdetails.json modified by Team2 to include 'sugar' in nutrients.
	"""
	filehandler = open('dishnames.csv', 'r')
	data = csv.reader(filehandler)

	finalResult = []

	for line in data:
		url = line[5]
		url = "http://www." + url
		page = urlopen(url)
		soup = BeautifulSoup(page, "lxml")
		print(url + ".................." + line[0])

		try:
			ingredientsList = []
			ingredientsSection = soup.find('section', {'class', 'recipe-ingredients'})
			listSection = ingredientsSection.find_all('ul', {'class', 'checklist'})
			for i in listSection:
				individualSection = i.find_all('span', {'class', 'recipe-ingred_txt'})
				for j in individualSection:
					ingredientsList.append(j.text.strip())
			ingredientsList = list(set(ingredientsList) - {'Add all ingredients to list', ''}) # Final
			print(ingredientsList)

			directionsSection = soup.find('div', {'class', 'directions--section__steps'})
			directions        = directionsSection.find_all('span', {'class', "recipe-directions__list--item"})
			directions        = directions[:len(directions) - 1]
			directionsList    = [i.text.strip() for i in directions] # Final
			print(directionsList)

			prepTime = "0" # Final
			cookTime = "0" # Final
			totalTime = "0" # Final

			prepTimeSection = directionsSection.find('ul', {'class', 'prepTime'})

			if len(prepTimeSection()) == 0:
				pass

			else:
				prepTimeList = prepTimeSection.text.strip().split("\n\n\n")
				
				for i in prepTimeList:
					if i.startswith("Prep"):
						prepTime = i[len("Prep"):]

					elif i.startswith("Cook"):
						cookTime = i[len("Cook"):]

					else:
						totalTime = i[len("Ready In"):]

			print(prepTime)
			print(cookTime)
			print(totalTime)

			nutrientSection = soup.find('section', {'class' : 'recipe-nutrition'})
			if nutrientSection != None:
				nutrientSection = nutrientSection.find('div', {'class' : 'recipe-nutrition__form'})
				nutrientList 	= nutrientSection.find_all('ul', {'class', 'nutrientLine'})
				allNutrients = []
				for i in nutrientList:
					a = i.find('li', {'class', 'nutrientLine__item'})
					if a == None:
						a = "Sodium: "
					else:
						a = a.text
					b = i.find('li', {'class', 'nutrientLine__item--amount'}).text
					c = i.find('li', {'class', 'nutrientLine__item--percent'}).text
					allNutrients.append([a, b, c])
				allNutrients = list(map(lambda x: [x[0][:x[0].index(":")], x[1], x[2]], allNutrients))
				allNutrients = OrderedDict([(i[0], [i[1], i[2]]) for i in allNutrients]) # Final
				print(allNutrients)
			else:
				allNutrients = {}

			finalResult.append(OrderedDict([("dish_id", int(line[0])), ("dish_name", line[1]), ("description", line[2]), ("overall_rating", float(line[3])), ("image_url", line[4]), ("url", url), ("ingredients", ingredientsList), ("directions", directionsList), ("prep_time", prepTime), ("cook_time", cookTime), ("total_time", totalTime), ("nutrients", allNutrients)]))

			summary = soup.find('div', {'class':"summary-stats-box"})

			reviewCount = summary.find('span', {'class':'review-count'})
			reviewCount = reviewCount.text.strip()
			reviewCount = int(reviewCount[:reviewCount.index(' ')])

			if reviewCount == 0:
				pass

			else:
				pass

		except:
			with open("exceptions.txt", "a") as exception:
				exception.write(line[0] + "," + line[1] + "," + line[5] + "\n")

			continue

	json.dump(finalResult, open("itemdetails.json", "w+"), indent = 4)


def get_reviews():
	"""
	NOTE : defunct function, using Team2 code

	Scrape reviews, by simulating a user session dynamically using selenium

	Input  - dishenames.csv
	Output - reviews.csv
	"""
	from selenium import webdriver
	from selenium.common.exceptions import NoSuchElementException
	from selenium.common.exceptions import ElementNotVisibleException
	from selenium.common.exceptions import WebDriverException

	driver = webdriver.Chrome('./chromedriver')

	filehandler = open('dishes.csv', 'r')
	data = csv.reader(filehandler)

	# reviewCounts = []

	for line in data:
		url = line[5]
		url = "http://www." + url

		driver.get(url)

		review = driver.find_element_by_class_name('review-count')
		totalReviews = int(review.text.strip().split()[0])

		# reviewCounts.append([int(line[0]), line[1], totalReviews])

		print(line[0], line[1])
		print("Total Reviews " + str(totalReviews))
		
		reviewCount = [int(line[0]), line[1], totalReviews]

		with open('review_counts.csv', 'a+') as filehandler_counts:
			filehandler_counts_writer = csv.writer(filehandler_counts)
			filehandler_counts_writer.writerow(reviewCount)

		allReviews = []
		if totalReviews > 0 and totalReviews < 300:
			review.click()
			time.sleep(3)
			for i in range(1, totalReviews + 1):
				
				print("Review", i)

				reviewText = driver.find_element_by_class_name('ReviewText').text
				print(reviewText)

				'''
				x = driver.find_element_by_class_name('recipe-details-cook-stats-container')
				y = x.find_element_by_tag_name('ul')
				z = y.find_elements_by_tag_name('li')[1]
				w = z.find_element_by_tag_name('h4')
				name = w.get_attribute('innerHTML').strip()

				print(name)
				'''

				x = driver.find_element_by_class_name('statsCard')
				y = x.find_elements_by_tag_name('li')
				z = y[1].find_element_by_tag_name('h4')
				name = z.text.strip()

				print("Reviewer Name :-", name)

				ratingSection = driver.find_element_by_class_name('rating')
				stars = ratingSection.find_elements_by_tag_name('img')
				rating = [i.get_attribute('src') for i in stars]
				rating = rating.count('http://images.media-allrecipes.com/ar-images/icons/rating-stars/full-star-2015.svg')
				print("Review Rating :-", rating)
				print("--------------------")

				for x in range(2, 4):
					try:
						nextButton = driver.find_element_by_id("BI_loadReview" + str(x) + "_right")
						break
					except ElementNotVisibleException:
						continue

				try:
					nextButton.click()
				except WebDriverException:
					closeButtons = ["bx-close-x-adaptive-1", "bx-close-x-adaptive-2", "fsrCloseBtn"]
					for i in closeButtons:
						try:
							close_x = driver.find_element_by_class_name(i)
						except ElementNotVisibleException:
							continue
						close_x.click()
						nextButton.click()

				allReviews.append([int(line[0]), name, rating, reviewText])

				time.sleep(1)

				if i == 1:
					time.sleep(5)

			filehandler_reviews = csv.writer(open('reviews.csv', 'a+'))
			filehandler_reviews.writerows(allReviews)

		else:
			with open('failed.csv', 'a+') as filehandler_falied:
				filehandler_failed_writer = csv.writer(filehandler_falied)
				filehandler_failed_writer.writerow([int(line[0]), line[1], totalReviews, line[5]])

def hash_user_id():
	"""
	Convert the user IDs from allrecipes and GForm to continuous UserIDs starting from 0

	NOTE : The reviews collected from the GForm need to be manually added to the reviews.csv file

	Input  - reviews.csv
	Output - review.csv
	"""
	data = csv.reader(open('reviews.csv', 'r'))

	data = list(data)[1:]

	user_dict = {}

	user_id = 0

	result = [['dishId', 'userId', 'rating']]

	for line in data:
		if line[1] in user_dict:
			userId = user_dict[line[1]]

		else:
			user_dict[line[1]] = user_id
			userId = user_id
			user_id += 1

		result.append([int(line[0]), int(userId), int(line[2])])

	fh = csv.writer(open("review.csv", 'w+'))
	fh.writerows(result)

def dish_name_csv():
	"""
	generate a mapping from dishId to dishName 

	Input  - itemdetails.json
	Output - id_name_mapping.csv
	"""
	data = json.load(open('itemdetails.json', 'rb'))

	final = [['dishId', 'dishName']]
	for i in data:
		final.append([i['dish_id'], i['dish_name']])

	fh = csv.writer(open('id_name_mapping.csv', 'w+'))
	fh.writerows(final)