import json
import re
from kb import Rejector
import unicodedata
import difflib
import math
import copy
from nltk import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import random
import utilities
import itertools
import user
import utilities
import itertools
import os


SWEET_FACTOR_X = 0.9
SWEET_FACTOR_Y = 0.1

RICHNESS_FACTOR_X = 0.5
RICHNESS_FACTOR_Y = 0.7
RICHNESS_FACTOR_Z = 50

SOURNESS_FACTOR_X = 0.1
SOURNESS_FACTOR_Y = 0.25
SOURNESS_FACTOR_Z = 0.5

p = PorterStemmer()
rejector = Rejector()
stop_words = set(stopwords.words('english'))


def strip_accents(s):
  return ''.join(c for c in unicodedata.normalize('NFD', s)
                 if unicodedata.category(c) != 'Mn')


def sweet(nutrition_data, SWEET_FACTOR_X=0.85, SWEET_FACTOR_Y=0.1):
  try:
    total_weight = nutrition_data['weight']
    fibtg = 0
    if 'dietary_fiber' in nutrition_data and nutrition_data['dietary_fiber'] is not None:
      fibtg = nutrition_data['dietary_fiber']
    sweet_score_x1 = abs(nutrition_data['sugar'] - fibtg) / total_weight
    sweet_score_y = nutrition_data['sugar'] / nutrition_data['carbs']
    sweet_score_1 = (SWEET_FACTOR_X * sweet_score_x1) + \
                    (SWEET_FACTOR_Y * sweet_score_y)

  except KeyError:
    sweet_score_1 = 0
  return round(sweet_score_1 / 0.998, 3) * 10


def rich(nutrition_data,
         RICHNESS_FACTOR_X=0.5,
         RICHNESS_FACTOR_Y=0.7,
         RICHNESS_FACTOR_Z=50):
  try:
    total_weight = nutrition_data['weight']
    richness_score_x = 0
    if 'sat_fat' in nutrition_data:
      richness_score_x = nutrition_data['sat_fat'] / \
          nutrition_data['fat']  # high

    richness_score_y = nutrition_data['fat'] / total_weight  # low
    richness_score_z = 0
    if 'cholesterol' in nutrition_data and nutrition_data['cholesterol'] is not None:
      richness_score_z = nutrition_data['cholesterol'] / (total_weight * 1000)
    else:
      richness_score_z = 0 
    richness_score_1 = (RICHNESS_FACTOR_X * richness_score_x) + \
        (RICHNESS_FACTOR_Y * richness_score_y) + \
        (RICHNESS_FACTOR_Z * richness_score_z)
  except KeyError:
    richness_score_1 = 0

    # Normalize to butter which has highest score
  return round((richness_score_1 / 0.992), 3) * 10


def salt(dish_nutrition):
  totalweight = dish_nutrition['weight']
  if totalweight == 0:
    return 0

  return ((1000 * dish_nutrition['sodium'] / totalweight)) / 3.8758
def match_descriptors(dish_title, descriptor_dict):
  dish_split = dish_title.split(" ")
  final_scores = dict()
  for item in descriptor_dict:
    for pair in itertools.product(item['items'].items(),dish_split):
    #format ((descriptor, score), dish_word)
      if pair[0][0].lower() in pair[1].lower():
        try:
          final_scores[item["name"]] += pair[0][1]
        except KeyError:
          final_scores[item["name"]] = pair[0][1]
  return final_scores


def umami(food, nutrition_data, PROTEIN_SUPPLEMENT_MULTIPLIER = 0.80, VEGETABLES_MULTIPLIER = 2.40, MEAT_MULTIPLIER = 1.75):
  umami_descriptors = utilities.read_json("umami_descriptors.json") 
  descriptor_score = match_descriptors(food['ingredient_str'], umami_descriptors)
  #print(PROTEIN_SUPPLEMENT_MULTIPLIER, VEGETABLES_MULTIPLIER, MEAT_MULTIPLIER, end=': ')
  #print(list(nutrition_data))
  protein_score = nutrition_data['protein'] / nutrition_data['Weight']
  umamiscore = protein_score
  pairings = zip([PROTEIN_SUPPLEMENT_MULTIPLIER, VEGETABLES_MULTIPLIER, MEAT_MULTIPLIER], ["protein_supps", "vegetables", "meat"])
  for pair in pairings:
    #print(pair)
    #umamiscore = 1.5meat + 2veggies + 1protein_supps
    if descriptor_score.__contains__(pair[1]):
      umamiscore += pair[0] * descriptor_score[pair[1]] * 1
  return round(umamiscore, 3)

def sour(food, nutrition_data, SOURNESS_FACTOR_X=0.1, SOURNESS_FACTOR_Y=0.25, SOURNESS_FACTOR_Z=0.5):
  #total_weight = nutrition_data['total_carb'] + nutrition_data['protein'] + nutrition_data['total_fat']
  total_weight = nutrition_data['Weight']
  food_words = [word for word in food['ingredient_str'].upper().split(' ') if len(word) > 0]
  #print(food_words)
  try:
    vitamin_c = nutrition_data['vitamin_c']
  except KeyError as ke:
    vitamin_c = 0.0
  #print(vitamin_c)
  with open('sour.json') as f:
    sour = json.load(f)
    #print(sour)
  with open('too_sour.json') as f:
    too_sour = json.load(f)
  try:
    sour_score_x = vitamin_c / total_weight
  except ZeroDivisionError as zde:
    sour_score_x = 0

  sour_score_y = 0
  sour_score_z = 0

  for word in food_words:
    if word in sour[word[0]]:
      #print("found s", word)
      sour_score_y += 1
    if word in too_sour[word[0]]:
      sour_score_z += 1
  sour_score = round(((SOURNESS_FACTOR_X * sour_score_x) + (SOURNESS_FACTOR_Y * sour_score_y) + (SOURNESS_FACTOR_Z * sour_score_z)) / 0.995,3)
  #print(sour_score)
  if sour_score > 1 :
    sour_score = 1
  return sour_score * 10

def get_dishes():
  #with open('../Utilities/Database/database.json') as json_file:
  with open('new_db.json') as json_file:
    foods_list = json.load(json_file)
  return foods_list


def total_weight(dish_nutrition):
  totalweight = 0
  for nutrient in dish_nutrition:
    if (dish_nutrition[nutrient] is not None and
            'g' in dish_nutrition[nutrient][0]):
      number = re.findall('(\d+\.\d+|\d+)', dish_nutrition[nutrient][0])
      numeric_value = 0
      if len(number) > 0:
        numeric_value = float(number[0])

      totalweight += numeric_value

  return totalweight


def get_nutrients(food):
  nutrients = food['nutrients']
  totalweight = total_weight(nutrients)

  for nutrient in nutrients:
    if nutrients[nutrient] is not None:
      number = re.findall('\d+\.\d+', nutrients[nutrient][0])
      if len(number) > 0:
        nutrients[nutrient] = float(number[0])
      else:
        nutrients[nutrient] = 0
  nutrients['weight'] = totalweight
  return nutrients

def match_descriptors(dish_title, descriptor_dict):
    dish_split = dish_title.split(" ")
    final_scores = dict()
    for item in descriptor_dict:
        for pair in itertools.product(item['items'].items(), dish_split):
            if pair[0][0].lower() in pair[1].lower().strip():
                try:
                    final_scores[item["name"]] += pair[0][1]
                except KeyError:
                    final_scores[item["name"]] = pair[0][1]
    return final_scores

def total_nutrient_weight(dish_nutrition):
    return dish_nutrition['fat'] + dish_nutrition['carbs'] + dish_nutrition['protein']

def bitter(food, nutrition_data, LEVEL1_MULTIPLIER=0.80, LEVEL2_MULTIPLIER=1.40, MULTI_WORD_MULTIPLIER=2.3):
    bitter_descriptors = utilities.read_json("bitter_descriptors.json")
    descriptor_score = match_descriptors(food['ingredient_str'], bitter_descriptors)
    bitterscore = nutrition_data["iron"] / total_nutrient_weight(nutrition_data)
    pairings = zip([LEVEL1_MULTIPLIER, LEVEL2_MULTIPLIER, MULTI_WORD_MULTIPLIER], ["bitter_l1", "bitter_l2", "multi_words"])
    for pair in pairings:
        if descriptor_score.__contains__(pair[1]):
            bitterscore += pair[0] * descriptor_score[pair[1]] * 1
    return round(bitterscore / 1.4571, 3)

def sour(food,
         nutrition_data,
         SOURNESS_FACTOR_X=0.1,
         SOURNESS_FACTOR_Y=0.25,
         SOURNESS_FACTOR_Z=0.5):

    total_weight = nutrition_data['carbs'] + \
        nutrition_data['protein'] + nutrition_data['fat']
    food_words = food['ingredient_str'].upper().split(' ')

    try:
        vitamin_c = nutrition_data['vitamin_c']
    except KeyError:
        vitamin_c = 0.0

    with open('sour.json') as f:
        sour = json.load(f)

    with open('too_sour.json') as f:
        too_sour = json.load(f)
    try:
        sour_score_x = vitamin_c / total_weight
    except ZeroDivisionError:
        sour_score_x = 0

    sour_score_y = 0
    sour_score_z = 0

    for word in food_words:
        if word in sour[word[0]]:
            sour_score_y += 1
        if word in too_sour[word[0]]:
            sour_score_z += 1
    sour_score = round(
        ((SOURNESS_FACTOR_X * sour_score_x) +
         (SOURNESS_FACTOR_Y * sour_score_y) +
         (SOURNESS_FACTOR_Z * sour_score_z)
         ) / 0.995, 3)
    if sour_score > 1:
        sour_score = 1
    return round(sour_score * 10, 3)

def umami(food,
          nutrition_data,
          PROTEIN_SUPPLEMENT_MULTIPLIER=0.80,
          VEGETABLES_MULTIPLIER=10,
          MEAT_MULTIPLIER=10,
          STRING_MULTIPLIER=9.45):
    for key in nutrition_data.keys():
        if nutrition_data[key] is None:
            nutrition_data[key] = 0
    umami_descriptors = utilities.read_json("umami_descriptors.json")
    descriptor_score = match_descriptors(food['ingredient_str'], umami_descriptors)

    umamiscore = nutrition_data["protein"] / total_nutrient_weight(nutrition_data)
    umamiscore *= 10

    pairings = zip([PROTEIN_SUPPLEMENT_MULTIPLIER, VEGETABLES_MULTIPLIER
                   , MEAT_MULTIPLIER, STRING_MULTIPLIER],
                   ["protein_supps", "vegetables",
                   "meat", "savory_strings"])
    for pair in pairings:
        if descriptor_score.__contains__(pair[1]):
            umamiscore += pair[0] * descriptor_score[pair[1]]

    return round(umamiscore, 3) if umamiscore <= 10 else 10


def taste(food):
# <<<<<<< HEAD
#   taste_scores = dict()
#   nutrients = get_nutrients(food)
#   salt_score = salt(nutrients)
#   taste_scores['salt'] = salt_score
#   sweet_score = sweet(nutrients)
#   taste_scores['sweet'] = sweet_score
#   richness_score = rich(nutrients)
#   taste_scores['rich'] = richness_score
#   umami_score = umami(food,nutrients)
#   taste_scores['umami'] = umami_score
#   sour_score = sour(food,nutrients)
#   taste_scores['sour'] = sour_score
#   tags = get_cuisine_tags(food['dish_name'])
#   cuisine_multipliers = get_cuisine_multipliers(tags)
#   taste_scores = update_scores(taste_scores, cuisine_multipliers)
#   return taste_scores
# =======
    nutrients = get_nutrients(food)
    tastes = {
        "salt": salt(nutrients),
        "sweet": sweet(nutrients),
        "rich": rich(nutrients),
        "umami": umami(food, nutrients),
        "sour": sour(food, nutrients),
        "bitter": bitter(food, nutrients)
    }
    if not os.path.exists("../Utilities/Team 2"):
        os.mkdir("../Utilities/Team 2")
    with open("../Utilities/Team 2/tastes.csv", "a") as csvfile:
        csvfile.write(",".join([str(food['dish_id'])] +
                               [str(round(tastes[key], 3))
                                for
                                key in
                                sorted(tastes.keys())]
                               )
                       + "\n")
    return tastes
#>>>>>>> 4900a75db52ee5543bd547efeb95c75359091329


def update_scores(taste_scores, cuisine_multipliers):
  for taste in taste_scores:
    taste_scores[taste] = taste_scores[taste] * cuisine_multipliers[taste]
  return taste_scores


def get_cuisine_multipliers(tags):
  with open('cuisine_multipliers.json') as json_file:
    cuisine_multipliers = json.load(json_file)
  default = {
      "salt": 1.0,
      "sweet": 1.0,
      "rich": 1.0
  }
  if tags is not None:
    if len(tags) == 0:
      return default
    if len(tags) == 1:
      return cuisine_multipliers[tags[0]]
    elif len(tags) == 2:
      return cuisine_multipliers[tags[0]][tags[1]]
  else:
    return default


def parse_recipe(food):
  ingredients_list = list(set(food['ingredients']))
  parsed_ingredients = list()
  for ing in ingredients_list:
    ingredient = identify_measurement(ing)
    parsed_ingredients.append(ingredient)
# <<<<<<< HEAD
#   #print(parsed_ingredients)
# =======
#   # print(parsed_ingredients)
# >>>>>>> 4900a75db52ee5543bd547efeb95c75359091329
  return parsed_ingredients


measurements = [
    "tablespoon",
    "tbsp",
    "tbs",
    "teaspoon",
    "tsp",
    "ts",
    "lb",
    "pound",
    "cup",
    "clove",
    "quart",
    "g",
    "gm",
    "gram",
    "ml",
    "ounce",
    "sprig",
    "oz",
    "clove",
    "cups",
    "lbs",
    "dash",
    "pinch",
    "pint"
]

adjectives = [
    "large",
    "medium",
    "small",
    "diced",
    "chopped",
    "minced",
    "crushed",
    "fresh",
    "warm",
    "sliced",
    "thinly",
    "finely",
    "divided",
    "dried",
    "peeled",
    "cubed",
    "halved",
    "ground",
    "frozen",
    "coarsely",
    "roughly",
    "pressed",
    "drained",
    "canned",
    "thawed",
    "quartered",
    "plain",
    "shredded",
    "cored",
    "grated",
    "slivered"
]


def convert_to_float(numeric_value):
  number = 0.0
  numeric_value = re.split('\s+', numeric_value)
  if len(numeric_value) == 2:
    fraction = numeric_value[1].split('/')
    number += float(numeric_value[0])
  else:
    fraction = numeric_value[0].split('/')
  number += float(fraction[0]) / float(fraction[1])
  return number


vulgar_fraction_dict = {
    "½": " 1/2",
    "⅓": " 1/3",
    "⅔": " 2/3",
    "¼": " 1/4",
    "¾": "3/4",
    "⅛": " 1/8",
    "⅒": " 1/10"
}


def convert_vulgar_fractions(ingredient):
  for char in ingredient:
    if char in vulgar_fraction_dict:
      ingredient = ingredient.replace(char, vulgar_fraction_dict[char])
  return ingredient


def cleanup_str(ingredient):
  ingredient = strip_accents(ingredient)
  ingredient = re.sub(r'(-|\(|\)|\[|\]|\{|\}|&|@)', "", ingredient)
  ingredient_tokens = ingredient.split(' ')
  for word in ingredient_tokens:
    index = ingredient_tokens.index(word)
    if re.match('[a-zA-Z +]', word) and '.' in word:
      ingredient_tokens[index] = word.replace('.', '')
  return ' '.join(ingredient_tokens)


def identify_measurement(ingredient):
  pattern = r'(\d+\s+\d/\d|\d+/\d+)'
  ingredient_dict = dict()
  ingredient = convert_vulgar_fractions(ingredient)
  ingredient = cleanup_str(ingredient)
  numeric_value = re.match(pattern, ingredient.strip())
  if numeric_value is not None:
    number = convert_to_float(numeric_value.group(0))
    ingredient = re.sub(pattern, str(number), ingredient)

  ingredient_tokens = [i.strip()
                       for i
                       in ingredient.lower().split(' ')
                       if
                       i not in
                       stop_words
                       ]
  ingredient_tokens = [i.strip()
                       for i
                       in ingredient.lower().split(' ')
                       if i not in
                       adjectives
                       ]

  measurement = str()
  prev_word = str()
  for word in ingredient_tokens:
    if len(
        difflib.get_close_matches(word, measurements, cutoff=0.9)
    ) > 0:
      measurement = prev_word + ' ' + word

    prev_word = word
  if len(measurement) == 0:
    measurement = re.match('\d+(.\d+)?', ingredient)
    if measurement is not None:
      measurement = measurement.group(0)
    else:
      measurement = str()

  ingredient_tokens = [i.strip() for i in ingredient_tokens]
  ingredient = ' '.join(ingredient_tokens).strip()
  ingredient = ingredient.replace(measurement, '')
  ingredient = rejector.process(ingredient.upper())
  ingredient_dict['measurement'] = measurement
  ingredient_dict['ingredient'] = rejector.process(ingredient.lower())
  return ingredient_dict


def get_cuisine_tags(food):
  with open('cuisine_tags.json') as json_file:
    tags = json.load(json_file)
  closest_match = difflib.get_close_matches(food, list(tags), cutoff=0.7)
  if len(closest_match) > 0 and closest_match[0] in tags:
    return tags[closest_match[0]]
  else:
    closest_match = difflib.get_close_matches(food, list(tags), cutoff=0.4)
    if len(closest_match) > 0 and closest_match[0] in tags:
      return tags[closest_match[0]]
    else:
      return ['unknown']
# def get_cuisine_tags(food_name):
#   with open('cuisine_tags.json') as json_file:
#     tags = json.load(json_file)
#   closest_match = utilities.modmatchi(food_name,list(tags),threshold=0.7)
#   #print(food['dish_name'],closest_match)
#   if closest_match[0] is not None:
#     try:
#       cuisine = tags[closest_match[0]]
#       if len(cuisine) == 2:
#         return cuisine[1]
#       elif len(cuisine) == 1:
#         return cuisine[0]
#     except Exception as e:
#       return 'unknown'
#   else:
#     return 'unknown'


def identify_cuisine(food, foods_list, vector, distance_metric):
  distances = dict()
  #print(food['dish_id'], food['ingredient_str'])
  # if distance_metric == jaccard_similarity:
  #   similarity = 0
  #   closest_dish = dict()
  #   for dish in foods_list:
  #     js = jaccard_similarity(food['ingredient_str'], dish['ingredient'])
  #     if js > similarity:
  #       similarity = js
  #       closest_dish = dish
  #   print(closest_dish)
  # else:
  food_bitstring = vector.toarray()[food['dish_id'] - 1]
  for index, bitstring in enumerate(vector.toarray()):
    if index != food['dish_id']:
      distances[(foods_list[index]['dish_name'])] = compare_distance(
          food_bitstring, bitstring, distance_metric)
  return sorted(distances.items(), key=lambda x: x[1], reverse=True)


def create_training_set(foods_list,test_set):
  training_set = list()
  total = 0
  count = dict()
  count['north indian'] = 0
  count['south indian'] = 0
  for food in test_set:
    item = dict()
    item['dish_name'] = food['dish_name']
    item['dish_id'] = total
    item['ingredient'] = food['ingredient_str']
    training_set.append(item)
    total += 1

  random.shuffle(foods_list)
  for food in foods_list:
    cuisine_tag = get_cuisine_tags(food['dish_name'])
    if len(cuisine_tag) > 0 and cuisine_tag[0] not in count:
      count[cuisine_tag[0]] = 0
    if total < 400 and len(cuisine_tag) > 0:
      item = dict()
      item['dish_name'] = food['dish_name']
      item['dish_id'] = total
      item['ingredient'] = food['ingredient_str']
      item['cuisine'] = cuisine_tag
      ''' probably use this to restrict amount of north indian tags
      if 'north indian' in cuisine_tag and count['north indian'] < 61:
        count['north indian'] += 1
        training_set.append(item)
      elif 'south indian' in cuisine_tag and count['south indian'] < 61:
        count['south indian'] += 1
        training_set.append(item)
      else:
      '''
      count[cuisine_tag[0]] += 1
      training_set.append(item)
      total += 1
  #print(count)
  return training_set

def load_test_dishes(test_file):
  with open(test_file) as json_file:
    return json.load(json_file)

def append_parsed(foods_list):
  for food in foods_list:
    parsed_ingredients = parse_recipe(food)
    ingredient_str = ' '.join(
        line['ingredient'] for line in parsed_ingredients if len(line['ingredient']) > 0
    )
    all_recipes.append(ingredient_str)
    index = foods_list.index(food)
    foods_list[index]['parsed_ingredients'] = parsed_ingredients
    foods_list[index]['ingredient_str'] = ingredient_str
  return foods_list


def knn(neighbors_cuisines):
  nearest_neighbor_dict = dict()
  # for item in neighbors_cuisines:
  #   vote = item[0]
  #   nearest_neighbor_dict[key] = dict()
  #   nearest_neighbor_dict[key]['weight'] = 0.0
  # for item in neighbors_cuisines:
  #   key = item[0]
  #   if item[0] is None:
  #     key = 'unknown'
  #   nearest_neighbor_dict[key]['weight'] += item[1]
  #   total_weight += item[1]

  for item in neighbors_cuisines:
    key = item[0]
    if len(key) == 1:
      key = key[0]
      if key in nearest_neighbor_dict:
        nearest_neighbor_dict[key] += 1 / float(math.pow(item[1],2))
      else:
        nearest_neighbor_dict[key] = 1 / float(math.pow(item[1],2))
    elif len(key) == 2:
      if key[0] in nearest_neighbor_dict and key[1] in nearest_neighbor_dict:
        nearest_neighbor_dict[key[0]] = 1 / float(math.pow(item[1],2))
        nearest_neighbor_dict[key[1]] = 1 / float(math.pow(item[1],2))
      elif key[0] not in nearest_neighbor_dict:
        nearest_neighbor_dict[key[0]] = 1 / float(math.pow(item[1],2))
      else:
        nearest_neighbor_dict[key[1]] = 1 / float(math.pow(item[1],2))
  return sorted(nearest_neighbor_dict.items(),key= lambda x : x[1])


all_recipes = list()
vectorizer = CountVectorizer()

def main():
  foods_list = get_dishes()
  foods_list = append_parsed(foods_list)
  copy_foods_list = copy.deepcopy(foods_list)
  test_dishes = load_test_dishes('sample_five.json')
  test_dishes = append_parsed(test_dishes)
  #print(list(test_dishes[0]['ingredient_str']))
  uprofile = user.Profile(data=test_dishes, history=5)
  training_set = create_training_set(copy_foods_list,test_dishes)
  test_indices = [i['dish_id'] for i in training_set if 'cuisine' not in i]
  all_recipes = [i['ingredient'] for i in training_set]
  #vector = vectorizer.fit_transform(all_recipes)
  # for index in test_indices:
  #   test_dish = training_set[test_indices[index]]
  #   print(test_dish['dish_name'])
  #   neighbors = identify_cuisine(test_dish,
  #                              training_set,
  #                              vector,
  #                              cosine_similarity)
  #   #print(json.dumps(neighbors))
  #   #print(type(neighbors))
  #   neighbors_cuisines = [(get_cuisine_tags(dish_name[0]), dish_name[1])
  #                       for dish_name
  #                       in neighbors
  #                       ][:7]
  #   #print(json.dumps(neighbors_cuisines))
  #   #print(foods_list[dish_id]['dish_name'])
  #   d = knn(neighbors_cuisines)
  #   # print("The taste profile for the dish", test_dish['dish_name'],"is")
    # print(taste(test_dish))
  #  print("Probable classes are ")
   # print(json.dumps(d, indent='  '))
  print("User profile for the specifie")
  print(uprofile)



def compare_distance(vector1, vector2, distance_metric):
  return distance_metric(vector1, vector2)


def euclidean(vector1, vector2):
  return math.sqrt(
      sum(
          pow(a - b, 2) for a, b in zip(vector1, vector2)
      )
  )


def cosine_similarity(vector1, vector2):
  dot_product = sum(p * q for p, q in zip(vector1, vector2))
  magnitude = math.sqrt(
      sum([val ** 2
           for val
           in vector1
           ]
          )
  ) * math.sqrt(sum([val**2 for val in vector2]))
  if not magnitude:
    return 0
  return dot_product / magnitude


def jaccard_similarity(vector1, vector2):
  intersection_size = len(set(vector1).intersection(set(vector2)))
  union_size = len(set(vector1).union(set(vector2)))
  return intersection_size / float(union_size)


if __name__ == '__main__':
  main()
