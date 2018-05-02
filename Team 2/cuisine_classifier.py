"""
This module is used in identifying the cuisine a particular dish belongs
to. It does so by converting a dish's ingredients to a vectorized format
using the TF-IDF method, and then uses KNN with a choice of similarity
measure to get the cuisine.
"""
import sys
import copy
import json
import math
import random
import difflib
from sklearn.feature_extraction.text import CountVectorizer
import taster
from utilities import read_json

def get_cuisine_tags(food):
    """
    This retrieves the cuisine tags from the JSON file which contains the
    list of dishes with their tags.
    It first tries to get the closest matching dish name and then retrives
    the tags. Tries it at thresholds of 0.7 and falls back to 0.4.
    If the tag is not found, returns unknown

    Keyword arguments:
    food  --  The name of the dish

    Returns:
    A list that contains tags if a match is found
    ['unknown'] otherwise
    """
    with open('cuisine_tags.json') as json_file:
        tags = json.load(json_file)
    closest_match = difflib.get_close_matches(food, list(tags), cutoff=0.7)
    if len(closest_match) > 0 and closest_match[0] in tags:
        return tags[closest_match[0]]
    closest_match = difflib.get_close_matches(food, list(tags), cutoff=0.4)
    if len(closest_match) > 0 and closest_match[0] in tags:
        return tags[closest_match[0]]
    return ['unknown']


def get_neighbors(food, foods_list, vector, distance_metric, limit=100):
    """
    Returns a dictionary of dishes and their distance from the dish
    specified in descending order of distances

    Keyword arguments:
    food            --  The dish specified for finding neighbors
    foods_list      --  The list of all dishes
    vector          --  The list of dish vectors that are created for all
                        dishes from CountVectorizer. It is a numeric
                        representation of all dishes
    distance_metric --  A function object that is to be passed, that
                        compares two vectors, and gets the distance
    limit           --  Parameter that limits the top neighbors when
                        sorted by distance

    Returns:
    A sorted dictionary of dish_names that the distance as value
    """
    distances = dict()
    food_bitstring = vector.toarray()[food['dish_id'] - 1]
    for index, bitstring in enumerate(vector.toarray()):
        if index != food['dish_id']:
            distances[(foods_list[index]['dish_name'])] = compare_distance(
                food_bitstring, bitstring, distance_metric)
    return sorted(distances.items(), key=lambda x: x[1], reverse=True)[:limit]


def knn(neighbors_cuisines):
    """
    This is the weighted KNN algorithm that identifies the cuisines
    of the k closest neighbors.

    Keyword arguments:
    neighbors_cuisines  --  A list of tuples that contains the cuisine
                            tags and the distance from the target dish

    Returns:
    nearest_neighbor_dict  --  A dictionary that contains the cuisine
                               tag and the distance of the closest
                               obtained from the closest neighbor

    """
    nearest_neighbor_dict = dict()
    for item in neighbors_cuisines:
        key = item[0]
        if len(key) == 1:
            key = key[0]
            if key in nearest_neighbor_dict:
                nearest_neighbor_dict[key] += 1 / float(math.pow(item[1], 2))
            else:
                nearest_neighbor_dict[key] = 1 / float(math.pow(item[1], 2))
        elif len(key) == 2:
            if key[0] in nearest_neighbor_dict and key[1] in nearest_neighbor_dict:
                nearest_neighbor_dict[key[0]] = 1 / float(math.pow(item[1], 2))
                nearest_neighbor_dict[key[1]] = 1 / float(math.pow(item[1], 2))
            elif key[0] not in nearest_neighbor_dict:
                nearest_neighbor_dict[key[0]] = 1 / float(math.pow(item[1], 2))
            else:
                nearest_neighbor_dict[key[1]] = 1 / float(math.pow(item[1], 2))
    return sorted(nearest_neighbor_dict.items(), key=lambda x: x[1])


def compare_distance(vector1, vector2, distance_metric):
    """
    A function that employs a callback mechanism to compare the distance
    between two vectors

    Keyword arguments:
    vector1, vector2  --  The vectors to be compared
    distance_metric   --  A function object that is used to compare
                          distance

    Returns:
    Distance between the 2 vectors
    """
    return distance_metric(vector1, vector2)


def euclidean(vector1, vector2):
    """
    Implementation of Euclidean Distance

    Keyword arguments:
    vector1, vector2  --  The vectors to be compared

    Returns :
    Distance between the 2 vectors
    """
    return math.sqrt(
        sum(
            pow(a - b, 2) for a, b in zip(vector1, vector2)
        )
    )


def cosine_similarity(vector1, vector2):
    """
    Implementation of Cosine Similarity. It gets the dot product
    between the 2 vectors and divides by the square root of their
    magnitudes

    Keyword arguments:
    vector1, vector2  --  The vectors to be compared

    Returns :
    Distance between the 2 vectors
    """
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
    """
    Implementation of Jaccard similarity to get distance between the
    2 vectors

    Keyword arguments:
    vector1, vector2  --  The vectors to be compared

    Returns :
    Distance between the 2 vectors
    """
    intersection_size = len(set(vector1).intersection(set(vector2)))
    union_size = len(set(vector1).union(set(vector2)))
    return intersection_size / float(union_size)


def create_training_set(foods_list, test_set):
    """
    Creates a training set from the list of dishes with cuisine tags
    Appends the ingredient strings to help ease comparison
    Modifies the test set passed to bring it to a uniform format

    Keyword arguments:
    foods_list  --  List of all dishes from which the training set is
                    generated
    test_set    --  List of dishes to be used for testing

    Returns:
    training_set  -- List of dishes used
    """
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
      # Uncomment this to restrict amount of north indian tags
        # if 'north indian' in cuisine_tag and count['north indian'] < 61:
        #     count['north indian'] += 1
        #     training_set.append(item)
        # elif 'south indian' in cuisine_tag and count['south indian'] < 61:
        #     count['south indian'] += 1
        #     training_set.append(item)
        # else:
        #     count[cuisine_tag[0]] += 1
        #     training_set.append(item)
        #     total += 1

    return training_set


def classify_cuisine(
        all_dishes,
        test_dishes,
        similarity_measure=cosine_similarity):
    """
    Main function to be run to identify cuisine of test dishes
    Appends the parsed ingredients to each object in both the
    all_dishes and test_dishes for convenience
    Retrieves the distances from other dishes for a test dish,
    and uses KNN to identify cuisine based on the other dishes

    Keyword arguments:
    all_dishes          --  List of all dishes
    test_dishes         --  List of dishes used for testing
    similarity_measure  --  Function object that is used as a
                            callback. Default is cosine_similarity

    Returns:
    cuisines_dict  --  A dictionary that contains the dish and its
                       predicted cuisine
    """
    foods_list = list()
    test_list = list()
    for food in all_dishes:
        foods_list.append(taster.append_parsed(food))
    for food in test_dishes:
        test_list.append(taster.append_parsed(food))
    copy_foods_list = copy.deepcopy(foods_list)
    cuisines_dict = dict()
    training_set = create_training_set(copy_foods_list, test_dishes)
    test_indices = [i['dish_id'] for i in training_set if 'cuisine' not in i]
    all_recipes = [i['ingredient'] for i in training_set]
    vector = vectorizer.fit_transform(all_recipes)
    for index in test_indices:
        test_dish = training_set[test_indices[index]]
        neighbors = get_neighbors(test_dish,
                                  training_set,
                                  vector,
                                  similarity_measure)
        neighbors_cuisines = [(get_cuisine_tags(dish_name[0]), dish_name[1])
                              for dish_name
                              in neighbors
                             ][:7]
        cuisines_dict[test_dish['dish_name']] = knn(neighbors_cuisines)
    return cuisines_dict


if __name__ == '__main__':
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        vectorizer = CountVectorizer()
        all_recipes = list()
        sample_size = 1300
        if len(sys.argv) == 4:
            sample_size = int(sys.argv[3])
        all_dishes = read_json(sys.argv[1])
        test_dishes = read_json(sys.argv[2])
        for dish, value in classify_cuisine(
                all_dishes[:sample_size],
                test_dishes,
                cosine_similarity).items():
            print(dish)
            print("------------")
            print(value)
            print()
    else:
        print("python3 cuisine_classifier.py <path_do_dish_database> <path_to_test_dishes> <sample_size>(OPTIONAL)")
