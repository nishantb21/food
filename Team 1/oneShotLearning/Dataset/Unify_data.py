import os
import json
from collections import Counter
file1 = '/home/unagi/IndianFoodRecognition/Dataset/dishes.csv'
file2 = '/home/unagi/IndianFoodRecognition/Dataset/itemdetails.json'
dishes = []
def getDishNames(file1,file2):
    with open(file1,'r') as infile:
        for line in infile:
            dishes.append(line.strip('\n'))
    jsonFile = json.load(open(file2))
    temp = [i['dish_name'] for i in jsonFile]
    for dish in temp:
        dishes.append(dish)


def main():
    getDishNames(file1,file2)
    dictDishes = dict(Counter(dishes))
    for k,v in dictDishes.items():
        if v > 1:
            print(k,v)
    with open('unified_list.txt','w') as outfile:
        for dish in dishes:
            outfile.write(dish+'\n')


if __name__ == '__main__':
    main()
