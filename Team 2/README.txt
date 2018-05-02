README - Flavour Profiling System (02/05/2018)

Overview:
==========
The Flavour Profiling System is capable of determining a dish's taste for
the following tastes : Bitter, Rich, Salt, Sour, Sweet and Umami, out of
10. It considers the dish's nutritional information and its ingredients
for calculation of these taste scores.
Also included in this project are:
- A web scraper for yummly.com, that retrieves data of a particular
  dish from the site, including ingredients, nutrition, reviews, etc.
- An ingredient parser, that is able to extract the ingredient and 
  their measurements from the list of ingredients
- A cuisine classifier, that determines the cuisine a dish belongs to
  based on the ingredients it comprises of.
- A validator, that generates a corrective adjustment for each of the
  tastes by comparing the generated and the surveyed flavour scores.

Installation:
=============
The system requires Python (version 3), and two external modules : nltk
and scikitlearn. 
Further Details about installation can be found in the User Guide

Execution:
==========
The system requires a JSON file that contains details of a dish, 
as specified in the schema below:
{
	dish_id: 1,
	dish_name: "chicken tikka masala",
	ingredients:["2 tsp salt",...],
	nutrients:{
		"sodium":["0.5g","24%"],
		"sat_fat":[...],
		"fat":[...],
		"cholesterol":[...],
		"sugar":[...],
		"carbohydrates":[...],
		"dietary_fiber":[...],
		"vitamin_c":[...],
		"protein":[...]
	},
	<other_details non essential to the system>
}

Run main.py:
- Specify '-p' or '--profile' and specify the path to the dish JSON file
  to generate the taste profile for the dish
  		python3 main.py --profile chicken_tikka_masala.json
  		{
  		 	'salt': 0.5852988548426411, 
  			'sweet': 0.55, 
  			'rich': 4.61, 
  			'umami': 7.31, 
  			'sour': 0.39, 
  			'bitter': 3.272
  		}
- Specify '-v' or '--validate', along with the taste and paths to the 
  generated and surveyed taste scores, to generate the adjustment factor for the dish
		python3 main.py [-v|--validate] <taste>[bitter|rich|sour|salt|sweet|umami] <path_to_generated_tastes> <path_to_surveyed_tastes>
		{
		    "bitter": 1.25,
		    "salt": -0.38,
		    "umami": 8.64,
		    "sour": 6.36,
		    "rich": -0.45,
		    "sweet": 0.02
		}

For information on how to run the other modules, read the User Guide
