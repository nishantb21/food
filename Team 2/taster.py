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
    total_weight = nutrition_data['Weight']
    fibtg = 0
    if 'Dietary_Fiber' in nutrition_data:
      fibtg = nutrition_data['Dietary_Fiber']
    sweet_score_x1 = abs(nutrition_data['Sugar'] - fibtg) / total_weight
    sweet_score_y = nutrition_data['Sugar'] / nutrition_data['Carbs']
    sweet_score_1 = (SWEET_FACTOR_X * sweet_score_x1) + \
                    (SWEET_FACTOR_Y * sweet_score_y)

  except Exception:
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
    if 'cholesterol' in nutrition_data:
      richness_score_z = nutrition_data['cholesterol'] / (total_weight * 1000)

    richness_score_1 = (RICHNESS_FACTOR_X * richness_score_x) + \
        (RICHNESS_FACTOR_Y * richness_score_y) + \
        (RICHNESS_FACTOR_Z * richness_score_z)
  except Exception:
    richness_score_1 = 0

    # Normalize to butter which has highest score
  return round((richness_score_1 / 0.992), 3) * 10


def salt(dish_nutrition):
  totalweight = dish_nutrition['Weight']
  if totalweight == 0:
    return 0

  return ((1000 * dish_nutrition['Sodium'] / totalweight)) / 3.8758


def get_dishes():
  with open('database.json') as json_file:
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
  nutrients['Weight'] = totalweight
  return nutrients


def taste(food):
  taste_scores = dict()
  nutrients = get_nutrients(food)
  salt_score = salt(nutrients)
  taste_scores['salt'] = salt_score
  sweet_score = sweet(nutrients)
  taste_scores['sweet'] = sweet_score
  richness_score = rich(nutrients)
  taste_scores['rich'] = richness_score
  tags = get_cuisine_tags(food['dish_name'])
  cuisine_multipliers = get_cuisine_multipliers(tags)
  taste_scores = update_scores(taste_scores, cuisine_multipliers)
  return taste_scores


def update_scores(taste_scores, cuisine_multipliers):
  print(cuisine_multipliers)
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
    return list()

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
  print(food['dish_id'], food['ingredient_str'])
  if distance_metric == jaccard_similarity:
    similarity = 0
    closest_dish = dict()
    for dish in foods_list:
      js = jaccard_similarity(food['ingredient_str'], dish['ingredient'])
      if js > similarity:
        similarity = js
        closest_dish = dish
    print(closest_dish)
  else:
    food_bitstring = vector.toarray()[food['dish_id'] - 1]
    for index, bitstring in enumerate(vector.toarray()):
      if index != food['dish_id']:
        distances[(foods_list[index]['dish_name'])] = compare_distance(
            food_bitstring, bitstring, distance_metric)
  return sorted(distances.items(), key=lambda x: x[1], reverse=True)


def create_training_set(foods_list):
  training_set = list()
  total = 0
  count = dict()
  count['north indian'] = 0
  count['south indian'] = 0

  sample = random.sample(foods_list, 400)
  for food in sample:
    cuisine_tag = get_cuisine_tags(food['dish_name'])
    if len(cuisine_tag) > 0 and cuisine_tag[0] not in count:
      count[cuisine_tag[0]] = 0
    if total < 400 and len(cuisine_tag) > 0:
      item = dict()
      item['name'] = food['dish_name']
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

  return training_set


def append_parsed(foods_list):
  for food in foods_list:
    parsed_ingredients = parse_recipe(food)
    ingredient_str = ' '.join(
        line['ingredient'] for line in parsed_ingredients
    )
    all_recipes.append(ingredient_str)
    index = foods_list.index(food)
    foods_list[index]['parsed_ingredients'] = parsed_ingredients
    foods_list[index]['ingredient_str'] = ingredient_str
  return foods_list


def knn(neighbors_cuisines):
  nearest_neighbor_dict = dict()
  total_weight = 0.0
  for item in neighbors_cuisines:
    key = item[0]
    if item[0] is None:
      key = 'unknown'
    nearest_neighbor_dict[key] = dict()
    nearest_neighbor_dict[key]['weight'] = 0.0
  for item in neighbors_cuisines:
    key = item[0]
    if item[0] is None:
      key = 'unknown'
    nearest_neighbor_dict[key]['weight'] += item[1]
    total_weight += item[1]

  for key in nearest_neighbor_dict:
    nearest_neighbor_dict[key]['weight'] /= total_weight
  return nearest_neighbor_dict


all_recipes = list()
vectorizer = CountVectorizer()


def main():
  foods_list = get_dishes()
  foods_list = append_parsed(foods_list)
  copy_foods_list = copy.deepcopy(foods_list)
  training_set = create_training_set(copy_foods_list)
  all_recipes = [i['ingredient'] for i in training_set]
  vector = vectorizer.fit_transform(all_recipes)
  dish_id = 1380
  print(foods_list[dish_id]['dish_name'])
  neighbors = identify_cuisine(foods_list[dish_id],
                               training_set,
                               vector,
                               jaccard_similarity)
  neighbors_cuisines = [(get_cuisine_tags(dish_name[0]), dish_name[1])
                        for dish_name
                        in neighbors
                        ]
  d = knn(neighbors_cuisines)
  print(json.dumps(d))


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
