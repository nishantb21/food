"""
Scans through the ingredients, removes unneeded words, adjectives and special
characters, accents, etc. Identifies the ingredient and its corresponding
measurement
"""
import re
import sys
import difflib
import unicodedata
from nltk.corpus import stopwords
from kb import Rejector
import utilities

rejector = Rejector()
stop_words = set(stopwords.words('english'))


def strip_accents(string):
    """
    Removes accented characters from a string by normalizing it

    Keyword arguments:
    s  --  String to be normalized

    Returns:
    Normalized string
    """
    return ''.join(char for char in unicodedata.normalize('NFD', string)
                   if unicodedata.category(char) != 'Mn')


def parse_recipe(food):
    """
    Parses the ingredient list present in the dish and returns a list of
    dictionary objects that contain the ingredient and its corresponding
    measurement

    Keyword arguments:
    food  --  Dictionary object that contains all details of a dish, like
              ingredients, nutrients, etc

    Returns:
    parsed_ingredients  --  A list of dictionary objects that contain the
                            ingredient and its corresponding measurement
    """
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
    """
    Given a fractional numeric value, converts it to a float

    Keyword arguments:
    numeric_value  --  The string that contains the fractional numeric value

    Returns:
    number  --  Floating point number that is the converted value
    """
    number = 0.0
    numeric_value = re.split(r'\s+', numeric_value)
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
    """
    Goes through each character in the ingredient and replaces the vulgar
    fractions with a readable string value

    Keyword arguments:
    ingredient  --  Ingredient strings for the given dish

    Returns:
    ingredient  --  String with the vulgar fraction replaced
    """
    for char in ingredient:
        if char in vulgar_fraction_dict:
            ingredient = ingredient.replace(char, vulgar_fraction_dict[char])
    return ingredient


def cleanup_str(ingredient):
    """
    Performs a cleanup of the string, removing special characters,
    non-alphanumeric characters, accents, etc

    Keyword arguments:
    ingredient  --  Ingredient strings for the given dish

    Returns:
    ingredient  --  Cleaned up ingredient string
    """
    ingredient = strip_accents(ingredient)
    ingredient = re.sub(r'(-|\(|\)|\[|\]|\{|\}|&|@)', "", ingredient)
    ingredient_tokens = ingredient.split(' ')
    for word in ingredient_tokens:
        index = ingredient_tokens.index(word)
        if re.match(r'[a-zA-Z +]', word) and '.' in word:
            ingredient_tokens[index] = word.replace('.', '')
    return ' '.join(ingredient_tokens)


def identify_measurement(ingredient):
    """
    Given an ingredient string, identifies the ingredient and the
    corresponding measurement by cleaning up the string and then
    matching ingredient and measurement patterns, etc.

    Keyword arguments:
    ingredient  --  Ingredient string for the given dish

    Returns:
    ingredient_dict  --  A dictionary object that contains the ingredient
                         and its corresponding measurement stored in the
                         respective keys
    """
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
        measurement = re.match(r'\d+(.\d+)?', ingredient)
        if measurement is not None:
            measurement = measurement.group(0)
        else:
            measurement = str()

    ingredient_tokens = [i.strip() for i in ingredient_tokens]
    ingredient = ' '.join(ingredient_tokens).strip()
    ingredient = ingredient.replace(measurement, '')
    ingredient = rejector.process(ingredient)
    ingredient_dict['measurement'] = measurement
    ingredient_dict['ingredient'] = rejector.process(ingredient)
    return ingredient_dict


if __name__ == '__main__':
    for file in sys.argv[1:]:
        for item in utilities.read_json(file):
            print(parse_recipe(item))
