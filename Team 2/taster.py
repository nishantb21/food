import os
import re
import sys
import json
from itertools import product
import utilities
import ingredient_parser

SWEET_FACTOR_X = 0.9
SWEET_FACTOR_Y = 0.1

RICHNESS_FACTOR_X = 0.5
RICHNESS_FACTOR_Y = 0.7
RICHNESS_FACTOR_Z = 50

SOURNESS_FACTOR_X = 0.1
SOURNESS_FACTOR_Y = 0.25
SOURNESS_FACTOR_Z = 0.5


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
        if 'cholesterol' in nutrition_data and nutrition_data['cholesterol'] is not None:
            richness_score_z = nutrition_data['cholesterol'] / \
                (total_weight * 1000)
        else:
            richness_score_z = 0
        richness_score_1 = (RICHNESS_FACTOR_X * richness_score_x) + \
            (RICHNESS_FACTOR_Y * richness_score_y) + \
            (RICHNESS_FACTOR_Z * richness_score_z)
    except Exception:
        richness_score_1 = 0

        # Normalize to butter which has highest score
    return round((richness_score_1 / 0.992), 3) * 10


def salt(dish_nutrition):
    totalweight = dish_nutrition['weight']
    if totalweight == 0:
        return 0

    return ((1000 * dish_nutrition['sodium'] / totalweight)) / 3.8758


def total_weight(dish_nutrition):
    totalweight = 0
    for nutrient in dish_nutrition:
        if (dish_nutrition[nutrient] is not None and
                'g' in dish_nutrition[nutrient][0]):
            number = re.findall(r'(\d+\.\d+|\d+)', dish_nutrition[nutrient][0])
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
            number = re.findall(r'\d+\.\d+', nutrients[nutrient][0])
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
        for pair in product(item['items'].items(), dish_split):
            if pair[0][0].lower() in pair[1].lower().strip():
                try:
                    final_scores[item["name"]] += pair[0][1]
                except KeyError:
                    final_scores[item["name"]] = pair[0][1]
    return final_scores


def total_nutrient_weight(dish_nutrition):
    return dish_nutrition['fat'] + dish_nutrition['carbs'] + \
        dish_nutrition['protein'] + dish_nutrition['calcium'] + dish_nutrition['iron']


def bitter(
        food,
        nutrition_data,
        LEVEL1_MULTIPLIER=0.80,
        LEVEL2_MULTIPLIER=1.40,
        MULTI_WORD_MULTIPLIER=2.3):
    try:
        bitter_descriptors = utilities.read_json("bitter_descriptors.json")
        descriptor_score = match_descriptors(
            food['ingredient_str'], bitter_descriptors)
        bitterscore = nutrition_data["iron"] / \
            total_nutrient_weight(nutrition_data)
        pairings = zip([LEVEL1_MULTIPLIER, LEVEL2_MULTIPLIER, MULTI_WORD_MULTIPLIER], [
            "bitter_l1", "bitter_l2", "multi_words"])
        for pair in pairings:
            if descriptor_score.__contains__(pair[1]):
                bitterscore += pair[0] * descriptor_score[pair[1]] * 1
    except Exception:
        bitterscore = 0

    return round(bitterscore / 1.4571, 3)


def sour(food,
         nutrition_data,
         SOURNESS_FACTOR_X=0.5,
         SOURNESS_FACTOR_Y=0.15,
         SOURNESS_FACTOR_Z=0.35):

    food_words = food['ingredient_str'].upper().split(' ')

    try:
        vitamin_c = nutrition_data['vitamin_c'] * 1000
    except KeyError:
        vitamin_c = 0.0

    with open('sour.json') as sour_file:
        sour = json.load(sour_file)

    with open('too_sour.json') as too_sour_file:
        too_sour = json.load(too_sour_file)
    try:
        sour_score_x = vitamin_c / nutrition_data['weight']
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
        ) / 1.43, 3)
    if sour_score > 1:
        sour_score = 1
    return round(sour_score * 10, 3)


def umami(food,
          nutrition_data,
          PROTEIN_SUPPLEMENT_MULTIPLIER=0.80,
          VEGETABLES_MULTIPLIER=7,
          MEAT_MULTIPLIER=3,
          STRING_MULTIPLIER=9.45):
    for key in nutrition_data.keys():
        if nutrition_data[key] is None:
            nutrition_data[key] = 0
    umami_descriptors = utilities.read_json("umami_descriptors.json")
    descriptor_score = match_descriptors(
        food['ingredient_str'], umami_descriptors)
    try:
        umamiscore = nutrition_data["protein"] / \
            total_nutrient_weight(nutrition_data)
        # umamiscore *= 10

        pairings = zip([PROTEIN_SUPPLEMENT_MULTIPLIER,
                        VEGETABLES_MULTIPLIER,
                        MEAT_MULTIPLIER,
                        STRING_MULTIPLIER],
                       ["protein_supps",
                        "vegetables",
                        "meat",
                        "savory_strings"])
        for pair in pairings:
            if descriptor_score.__contains__(pair[1]):
                umamiscore += pair[0] * descriptor_score[pair[1]]
    except Exception:
        umamiscore = 0

    return round(umamiscore, 3) if umamiscore <= 10 else 10


def taste(food):
    food = append_parsed(food)
    nutrients = get_nutrients(food)
    tastes = {
        "salt": salt(nutrients),
        "sweet": sweet(nutrients),
        "rich": rich(nutrients),
        "umami": umami(food, nutrients),
        "sour": sour(food, nutrients),
        "bitter": bitter(food, nutrients)
    }
    if os.path.exists("adjustment_factors.json"):
        with open("adjustment_factors.json") as adjustments:
            for taste, adjustment in json.load(adjustments).items():
                tastes[taste] -= adjustment

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


def append_parsed(food):
    parsed_ingredients = ingredient_parser.parse_recipe(food)
    ingredient_str = ' '.join(
        line['ingredient'] for line in parsed_ingredients if len(
            line['ingredient']) > 0)
    # all_recipes.append(ingredient_str)

    food['parsed_ingredients'] = parsed_ingredients
    food['ingredient_str'] = ingredient_str
    return food


all_recipes = list()


def main():
        #foods_list = list()
        # for food in get_dishes():
        #    foods_list.append(append_parsed(food))
        # copy_foods_list = copy.deepcopy(foods_list)
        #test_dishes = list()
    for datafile in sys.argv[1:]:
        for item in utilities.load_dishes(datafile):
            taste(item)
    #uprofile = user.Profile(data=test_dishes, history=5)
    #   # print("The taste profile for the dish", test_dish['dish_name'],"is")
    # print(taste(test_dish))
    #  print("Probable classes are ")
    # print(json.dumps(d, indent='  '))
    #print("User profile")
    # print(uprofile)


if __name__ == '__main__':
    open("../Utilities/Team 2/tastes.csv", "w").close()
    main()
