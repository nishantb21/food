import json
import os

def main():
    my_path = os.path.abspath(os.path.dirname(__file__))
    parent_directory = os.path.abspath(os.path.dirname(my_path))
    database_path = os.path.join(parent_directory, 'Team 2', 'tastes.csv')
    with open(database_path, 'r') as infile:
        
    dish_list = []
    dish_mapping = {}
    for i in json_data:
        if i['dish_name'] not in dish_list:
            dish_list.append(i['dish_name'])
            dish_mapping[i['dish_name']] = i['dish_id']

    dictionary = {}
    dictionary['list'] = dish_list
    dictionary['mapping'] = dish_mapping
    print(json.dumps(dictionary))


if __name__ == '__main__':
    main()