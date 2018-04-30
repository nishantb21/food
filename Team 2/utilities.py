"""
This module consists of a list of utilities that are used throughout the
project.
"""
import re
import csv
import sys
import json
import hashlib
import datak


def standardize_keys(nutrition_information):
    """
    Standardize nutritional information
    Maps common nutrients to the standard format
    food_name: item_name
    serving_weight_grams:metric_qty
    nf_calories: calories
    nf_total_fat:total_fat
    nf_saturated_fat:saturated_fat
    nf_cholesterol: cholesterol
    nf_sodium:sodium
    nf_total_carbohydrates:total_carb
    nf_dietary_fiber:dietary_fiber
    nf_sugars:sugars
    nf_protein:protein
    """
    if nutrition_information.__contains__('metric_qty '):
        keys = [
            "item_name",
            "metric_qty",
            "calories",
            "total_fat",
            "saturated_fat",
            "cholesterol",
            "sodium",
            "total_carb",
            "dietary_fiber",
            "sugars",
            "protein"
        ]
        dictionary = dict()
        for key in keys:
            dictionary[key] = nutrition_information[key]
        dictionary["iron"] = nutrition_information["iron_dv"] \
            if nutrition_information["iron_dv"] is not None else 0
        return dictionary
    full_nutrient_keys = {"iron": 303, "vitamin_c": 401}
    full_nutrient_indices = {'iron': 0, 'vitamin_c ': 0}
    for nutrient in nutrition_information['full_nutrients']:
        for item in full_nutrient_keys.items():
            if nutrient['attr_id'] == item[1]:
                full_nutrient_indices[item[0]] = nutrition_information['full_nutrients'].index(
                    nutrient)

    standard_keys = [
        "food_name",
        "serving_weight_grams",
        "nf_calories",
        "nf_total_fat",
        "nf_saturated_fat",
        "nf_cholesterol",
        "nf_sodium",
        "nf_total_carbohydrate",
        "nf_dietary_fiber",
        "nf_sugars",
        "nf_protein"]
    common_keys = [
        "item_name",
        "metric_qty",
        "calories",
        "total_fat",
        "saturated_fat",
        "cholesterol",
        "sodium",
        "total_carb",
        "dietary_fiber",
        "sugars",
        "protein"]
    mappings = zip(standard_keys, common_keys)
    new_nutrition_information = dict()
    for mapping in mappings:
        new_nutrition_information[mapping[1]
                                  ] = nutrition_information[mapping[0]]
    for item in full_nutrient_indices.items():
        try:
            new_nutrition_information[item[0]
                                      ] = nutrition_information['full_nutrients'][item[1]]["value"]
        except IndexError:  # c as ie:
            new_nutrition_information[item[0]] = 0.0
    return new_nutrition_information


def read_csv(csv_file):
    """
    Reads the CSV file, and writes every row to a readable JSON file
    for easier parsing. (Used if the food data is in a CSV file)
    """
    with open(csv_file) as c_file:
        reader = csv.reader(c_file, delimiter=",")
        next(reader)
        txt_file = open('food_names.txt', 'w')
        for row in reader:
            name = row[0].strip()
            txt_file.write(name + '\n')
            item_dict = dict()
            item_dict['name'] = name
            item_dict['ingredients'] = eval(row[15].strip())
            name_hash = hash(name)
            with open('hashed_foods/' + name_hash + '.json', 'w') as dish_file:
                json.dump(item_dict, dish_file, indent='\t')
    txt_file.close()


def parameterize(qstring):
    """
    Converts string to a format that can be used in a search URL
    """
    return qstring.strip('\n').replace(' ', '+')


def modmatchir(query_string, nriterable, threshold):
    """
    From a list of strings, retrieves the best matching string

    Keyword arguments:
    query_string  --  String to find a match
    nriterable    --  List of strings to find a match from
    threshold     --  Match % to check while searching

    Returns:
    The best matched String
    None if the iterable is empty or not found
    """
    if len(nriterable) == 0:
        return None
    best_match = (None, -1)
    best_match_index = 0
    current_index = -1
    for word in nriterable:
        result = modmatch(query_string, word.name, threshold)
        current_index += 1
        if result is not None and result[1] > best_match[1]:
            best_match_index = current_index
            best_match = result
    return nriterable[best_match_index]


def modmatchi(query_string, iterable, threshold):
    """
    From a list of strings, retrieves the best matching string

    Keyword arguments:
    query_string  --  String to find a match
    iterable      --  List of strings to find a match from
    threshold     --  Match % to check while searching

    Returns:
    The best matched String
    None if the iterable is empty or not found
    """
    best_match = (None, -1)
    for word in iterable:
        result = modmatch(query_string, word, threshold)
        best_match = result if result is not None and result[1] > best_match[1] else best_match
    return best_match


def modmatch(query_string, match_string, threshold):
    """
    Function to compare two strings.
    Cleans up the strings and checks if the similarity is greater
    than or equal to the threshold. If true, returns the match_string
    and its similarity. Returns None if false

    Keyword arguments:
    query_string  --  String to find a match
    match_string  --  Strings to be matched
    threshold     --  Match % to check

    Returns:
    A tuple of string and the similarity if match is true
    None if false
    """
    match_string = re.sub(',', ' ', match_string)
    query_string = re.sub(', ', ' ', query_string)

    match_string_split = match_string.strip().upper().split('  ')
    query_string_split = query_string.strip().upper().split('  ')
    matched = [word for word in query_string_split if word in match_string_split]
    if len(matched) > 0 or ('  ' not in match_string and query_string.upper(
    ).strip() in match_string.upper().strip()):
        if len(matched) / len(query_string_split) >= threshold:
            return (
                match_string,
                round(
                    len(matched) /
                    len(query_string_split),
                    2))
    return None


def hash(input_title):
    """
    Returns an md5 hash of the string passed
    """
    return hashlib.md5(input_title.strip().strip(
        '\n').upper().encode('utf-8')).hexdigest()


def package(input_file):
    """
    TBD
    """
    contents = dict()
    with open(input_file) as ifile:
        for line in ifile:
            if not contents.__contains__(line[0]):
                contents[line[0]] = set()
            contents[line[0]].add(line.strip('\n '))

    for key in contents:
        contents[key] = list(contents[key])
    with open(input_file.split('. ')[0] + '.json ', 'w') as writer:
        json.dump(contents, writer, indent='\t ')


def standardize(input_file):
    """
    Standardizes the nutrition to the proper serving sizes,
    given an input file.
    food name: food_name
    serving size: serving_weight_grams
    fat:
        nf_total_fat
        nf_saturated_fat
    Salt: nf_sodium, nf_potassium
    sugar: nf_sugars
    protein: nf_protein
    calories: nf_calories
    ---pairwise calculation:
    carbs: nf_total_carbohydrate
    """
    nutrition_scrubbed = dict()

    with open('nutritionix_data/' + input_file) as json_file, \
            open('nutritionix_data/' + input_file + '_std', 'w') \
            as json_standardized:
        nutrition = json.load(json_file)
        if nutrition['serving_weight_grams'] is not None:
            multiplier = round(100 / nutrition['serving_weight_grams'], 3)
        else:
            return None
        print('\r', input_file, ':', multiplier, sep='', end='\r', flush=True)
        key_list = [
            'nf_calories',
            'nf_total_fat',
            'nf_cholesterol',
            'nf_sodium',
            'nf_total_carbohydrate',
            'nf_saturated_fat',
            'nf_dietary_fiber',
            'nf_sugars',
            'nf_protein',
            'nf_potassium']
        nutrition_scrubbed['food_name'] = nutrition['food_name']
        nutrition_scrubbed['nf_ndb_no'] = nutrition['ndb_no']
        nutrition_scrubbed['nf_upc'] = nutrition['upc']
        for key in key_list:
            nutrition_scrubbed[key] = round(
                nutrition[key] * multiplier,
                3) if nutrition[key] is not None else 0.0

        json.dump(nutrition_scrubbed, json_standardized, indent='\t')
        return json_standardized.name


def ratio(i_no=1):
    """
    Custom implementation of finding the ratio shared between a list
    of objects
    """
    fractal = round(100 / i_no, 4)
    perc_list = list()
    for index in range(i_no):
        perc_list.append(fractal)

    for rrange in range(1, i_no):
        steal = round(((rrange / i_no) * fractal) / 2, 4)
        perc_list[rrange] -= steal
        perc_list[0] += steal
    return perc_list


def standardize_files(file):
    """
    A function that standardizes the nutritional infomation in a file
    To a uniform format
    """
    nutri = dict()
    with open(file) as raw_file:
        nutri = json.load(raw_file)
    with open("fin/" + file.split("/")[-1], 'w') as stdfile:
        json.dump(standardize_keys(nutri), stdfile, indent='\t ')
        print('\r', file, end=' ')


def read_json(file):
    """
    Read from a JSON file
    """
    with open(file) as json_file:
        return json.load(json_file)


def split_title(input_title):
    """
    Removes stopwords and returns a list that contains the input title
    split into words
    """
    stopwords = [
        ' i',
        ' me',
        ' my',
        ' myself',
        ' we',
        ' our',
        ' ours',
        ' ourselves',
        ' you ',
        ' your ',
        ' yours ',
        ' yourself ',
        ' yourselves ',
        ' he ',
        ' him ',
        ' his ',
        ' himself ',
        ' she ',
        ' her ',
        ' hers ',
        ' herself ',
        ' it ',
        ' its ',
        ' itself ',
        ' they ',
        ' them ',
        ' their ',
        ' theirs ',
        ' themselves ',
        ' what ',
        ' which ',
        ' who ',
        ' whom ',
        ' this ',
        ' that ',
        ' these ',
        ' those ',
        ' am ',
        ' is ',
        ' are ',
        ' was ',
        ' were ',
        ' be ',
        ' been ',
        ' being ',
        ' have ',
        ' has ',
        ' had ',
        ' having ',
        ' do ',
        ' does ',
        ' did ',
        ' doing ',
        ' a ',
        ' an ',
        ' the ',
        ' and ',
        ' but ',
        ' if ',
        ' or ',
        ' because ',
        ' as ',
        ' until ',
        ' while ',
        ' of ',
        ' at ',
        ' by ',
        ' for ',
        ' with ',
        'without ',
        ' about ',
        ' against ',
        ' between ',
        ' into ',
        ' through ',
        ' during ',
        ' before ',
        ' after ',
        ' above ',
        ' below ',
        ' to ',
        ' from ',
        ' up ',
        ' down ',
        ' in ',
        ' out ',
        ' on ',
        ' off ',
        ' over ',
        ' under ',
        ' again ',
        ' further ',
        ' then ',
        ' once ',
        ' here ',
        ' there ',
        ' when ',
        ' where ',
        ' why ',
        ' how ',
        ' all ',
        ' any ',
        ' both ',
        ' each ',
        ' few ',
        ' more ',
        ' most ',
        ' other ',
        ' some ',
        ' such ',
        ' no ',
        ' nor ',
        ' not ',
        ' only ',
        ' own ',
        ' same ',
        ' so ',
        ' than ',
        ' too ',
        ' very ',
        ' s ',
        ' t ',
        ' can ',
        ' will ',
        ' just ',
        ' don ',
        ' should ',
        ' now ',
        ' d ',
        ' ll ',
        ' m ',
        ' o ',
        ' re ',
        ' ve ',
        ' y ',
        ' ain ',
        ' aren ',
        ' couldn ',
        ' didn ',
        ' doesn ',
        ' hadn ',
        ' hasn ',
        ' haven ',
        ' isn ',
        ' ma ',
        ' mightn ',
        ' mustn ',
        ' needn ',
        ' shan ',
        ' shouldn ',
        ' wasn ',
        ' weren ',
        ' won ',
        ' wouldn ',
    ]
    words = "|".join(stopwords)
    return [
        word.strip() for word in re.sub(
            words,
            "$$",
            input_title).split("$$") if word != '']


def add_sides(titles, main_title, save_to_file=False):
    """
    TBD
    """
    finaldish = dict()
    for subtitle in titles:
        ndata = datak.ingredient(subtitle)
        if not ndata["item_name"].lower() == subtitle.lower():
            print(ndata["item_name"], file=sys.stderr)
        for key, value in (
                (key, value) for key, value in ndata.nutrition_data.items() if isinstance(
                    value, (float, int))):
            try:
                finaldish[key] += ndata.nutrition_data[key]
            except KeyError:
                finaldish[key] = ndata.nutrition_data[key]

    if save_to_file:
        with open(hash(main_title) + ".json", "w") as mainfile:
            json.dump(finaldish, mainfile, indent="\t")
            print(hash(main_title) + ".json", file=sys.stderr)
    return finaldish


def get_dishes():
    """
    Load dishes from the database
    """
    with open('../Utilities/Database/database.json') as json_file:
        foods_list = json.load(json_file)
    return foods_list


if __name__ == '__main__':
    print(add_sides(sys.argv[1:len(sys.argv) - 1],
                    sys.argv[-1], save_to_file=True))
    # print(split_title(sys.argv[1]))
