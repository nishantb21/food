'''
Taste module
============
This is the main component of the entire system. It performs preprocessing
using the ingredient_parser module which converts various parts of the data
into a format used internally, as described in greater detail
in the documentation for that module.
'''

import os
import re
from itertools import product
import utilities
import ingredient_parser


def append_parsed(food):
    '''
    Obtains a list of ingredients along with their measurements
    and replaces the ingredient key-value pair with their parsed equivalents
    and returns the modified JSON object.
    '''
    parsed_ingredients = ingredient_parser.parse_recipe(food)
    ingredient_str = ' '.join(
        line['ingredient'] for line in parsed_ingredients if len(
            line['ingredient']) > 0)

    food['parsed_ingredients'] = parsed_ingredients
    food['ingredient_str'] = ingredient_str
    return food


def get_nutrients(food):
    '''
    Replaces the nutrients that are present in the food JSON object
    with nutrients that have been parsed and quantified.
    Adds another key-value pair into the JSON object for
    the total active nutritional weight of the food item.
    '''
    nutrients = food['nutrients']

    for nutrient in nutrients:
        if nutrients[nutrient] is not None:
            number = re.findall(r'\d+\.\d+', nutrients[nutrient][0])
            if len(number) > 0:
                nutrients[nutrient] = float(number[0])
            else:
                nutrients[nutrient] = 0

    totalweight = total_nutrient_weight(nutrients)
    nutrients['weight'] = totalweight
    return nutrients


def taste(food):
    '''
    The main public interface of the system.
    This function returns a JSON object that contains
    six taste scores, on a scale of 0 to 10:
    bitter, rich, salt, sour, sweet and umami
    '''
    food = append_parsed(food)
    nutrients = get_nutrients(food)
    tastes = {
        "bitter": bitter(food, nutrients),
        "rich": rich(nutrients),
        "salt": salt(nutrients),
        "sour": sour(food, nutrients),
        "sweet": sweet(nutrients),
        "umami": umami(food, nutrients)
    }
    if os.path.exists("adjustment_factors.json"):
        for taste, adjustment \
                in utilities.read_json("adjustment_factors.json").items():

            tastes[taste] -= adjustment

    if not os.path.exists("../Utilities/Team 2"):
        os.mkdir("../Utilities/Team 2")
    with open("../Utilities/Team 2/tastes.csv", "a") as csvfile:
        csvfile.write(",".join([str(food['dish_id'])] +
                               [str(round(tastes[key], 3))
                                for
                                key in
                                sorted(tastes.keys())]
                               ) + "\n")
    return tastes


def bitter(food,
           nutrition_data,
           LEVEL1_MULTIPLIER=0.80,
           LEVEL2_MULTIPLIER=1.40,
           MULTI_WORD_MULTIPLIER=2.3):
    '''
    This function computes the bitter score for the food item.
    This computation is performed with three approaches:
    - The iron content is used a fraction of the total active nutrient weight
    - Three groups of descriptors are used, each of which
        has a different weightage towards the final scoring.
    - The bitter words are divided into two levels, each corresponding
        to an particular intensity of bitterness. Each of these levels
        again has a different weightage.

    Finally, a real value from 0-10 is returned as a bitter score
    for the food item.
    '''
    try:
        bitter_descriptors = utilities.read_json("bitter_descriptors.json")
        descriptor_score = match_descriptors(
            food['ingredient_str'], bitter_descriptors)
        bitterscore = (nutrition_data["iron"] /
                       total_nutrient_weight(nutrition_data))
        pairings = zip([LEVEL1_MULTIPLIER,
                       LEVEL2_MULTIPLIER,
                       MULTI_WORD_MULTIPLIER],
                       ["bitter_l1",
                       "bitter_l2",
                       "multi_words"])
        for pair in pairings:
            if descriptor_score.__contains__(pair[1]):
                bitterscore += pair[0] * descriptor_score[pair[1]] * 1
    except Exception:
        bitterscore = 0

    return round(bitterscore / 1.4571, 3)


def rich(nutrition_data,
         RICHNESS_FACTOR_X=0.5,
         RICHNESS_FACTOR_Y=0.7,
         RICHNESS_FACTOR_Z=50):
    '''
    This function computes the rich score for the food item.
    This computation is performed with three approaches:
    - The saturated fat content is used as
        a fraction of the actual fat content present in the food item
    - Another metric measures the actual fat content as a fraction
        of the total active nutritional weight
    - The amount of cholesterol is also taken into account while
        calculating the rich score. This metric has the highest impact
        on the final output.

    Each of the above metrics has a tunable weight assigned to it,
    which determines how much that metric influences the outcome
    of the function.

    Finally, a real value from 0-10 is returned as a rich score
    for the food item.
    '''
    try:
        total_weight = nutrition_data['weight']
        richness_score_x = 0
        if 'sat_fat' in nutrition_data:
            richness_score_x = nutrition_data['sat_fat'] / \
                nutrition_data['fat']  # high

        richness_score_y = nutrition_data['fat'] / total_weight
        richness_score_z = 0
        if ('cholesterol' in nutrition_data and
                nutrition_data['cholesterol'] is not None):
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
    '''
    Calculation of the salt score is pretty straightforward
    since the amount of sodium directly affects how salty a dish
    can be perceived by a user.
    Therefore, to compute the salt score, the fraction of sodium content in
    the total active nutritional weight is taken directly.

    This score is normalized wrt amount of sodium in pure sea salt.

    '''
    totalweight = dish_nutrition['weight']
    if totalweight == 0:
        return 0

    saltscore = (1000 * dish_nutrition['sodium'] / totalweight) / 3.8758

    if saltscore > 10:
        return 10
    return saltscore


def sour(food,
         nutrition_data,
         SOURNESS_FACTOR_X=0.5,
         SOURNESS_FACTOR_Y=0.15,
         SOURNESS_FACTOR_Z=0.35):
    '''
    For sourness, an approach similar to how bitter was calculated
    is applied.
    Here, the nutrient directly affecting the sourness of a food item
    is the vitamin C content. Therefore, this is given the maximum weightage
    of 50% that counts towards the final final sour score for the dish.

    The other two metrics are calculated from comparing against
    an internally maintained database of ingredients and keywords,
    each of which is given its own weightage. These are divided
    into two levels: sour and too sour. Naturally, too sour keywords have
    a higher weightage than keywords that are tagged just sour.
    '''
    food_words = food['ingredient_str'].upper().split(' ')

    try:
        vitamin_c = nutrition_data['vitamin_c'] * 1000
    except KeyError:
        vitamin_c = 0.0

    sour = utilities.read_json("sour.json")
    too_sour = utilities.read_json("too_sour.json")
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


def sweet(nutrition_data, SWEET_FACTOR_X=0.85, SWEET_FACTOR_Y=0.1):
    '''
    Calculation of sweet scores is relatively straightforward,
    similar to how salt score is calculated. here, the amount of sugar
    as a fraction of the total nutritional weight.
    Along with this metric, the diluting effect of fiber is also
    taken into account.
    '''
    try:
        total_weight = nutrition_data['weight']
        fibtg = 0
        if ('dietary_fiber' in nutrition_data and
                nutrition_data['dietary_fiber'] is not None):
            fibtg = nutrition_data['dietary_fiber']

        sweet_score_x1 = abs(nutrition_data['sugar'] - fibtg) / total_weight
        sweet_score_y = nutrition_data['sugar'] / nutrition_data['carbs']
        sweet_score_1 = (SWEET_FACTOR_X * sweet_score_x1) + \
                        (SWEET_FACTOR_Y * sweet_score_y)

    except Exception:
        sweet_score_1 = 0
    # Normalize to cane sugar
    return round(sweet_score_1 / 0.998, 3) * 10


def umami(food,
          nutrition_data,
          PROTEIN_SUPPLEMENT_MULTIPLIER=0.80,
          VEGETABLES_MULTIPLIER=7,
          MEAT_MULTIPLIER=3,
          STRING_MULTIPLIER=9.45):
    '''
    Calculation of umami score is similar to that of bitter -
    The presense of iron along with the added effects of different
    categories of keywords, such as savoury vegetables,
    the savouriness of different meats as well as
    naturally occuring sources of protein, such as casein,
    all have their own weights that determines their contribution
    to the final score.
    '''
    for key in nutrition_data.keys():
        if nutrition_data[key] is None:
            nutrition_data[key] = 0
    umami_descriptors = utilities.read_json("umami_descriptors.json")
    descriptor_score = match_descriptors(
        food['ingredient_str'], umami_descriptors)
    try:
        umamiscore = (nutrition_data["protein"] /
                      total_nutrient_weight(nutrition_data))

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


def match_descriptors(dish_title, descriptor_dict):
    '''
    Helper that matches predefined descriptor keywords
    in the actual dish.
    Returns a JSON object that contains the total weights
    of all the matched keyword descriptors.
    '''
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
    '''
    Returns the total active nutrient weight of the food item.
    '''
    return dish_nutrition['fat'] + dish_nutrition['carbs'] + \
        dish_nutrition['protein'] + \
        dish_nutrition['calcium'] + dish_nutrition['iron']
