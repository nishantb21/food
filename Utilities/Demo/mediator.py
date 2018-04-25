import sys
from pymongo import MongoClient
import csv
import os
import json
my_path = os.path.abspath(os.path.dirname(__file__))

'''
To run:
python3 mediator.py rating userID predictedDish
'''
def purify(data):
    for key in data.keys():
        if data[key] == None:
            data[key] = "None"

    return data

def getDocumentDetails(predictedDish):
    c = MongoClient()
    db = c.foodDatabase
    collection = db.itemDetails
    document = collection.find_one({'dish_name':predictedDish})
    dishID = document['dish_id']

    return dishID, document['nutrients']

def flavourDetails(dishID):
    my_path = os.path.abspath(os.path.dirname(__file__))
    parent_directory = os.path.abspath(os.path.dirname(my_path))
    database_path = os.path.join(parent_directory, 'Team 2', 'tastes.csv')
    with open(database_path, 'r') as infile:
        csv_data = list(csv.reader(infile))

    json_data = {}
    for row in csv_data: 
        if int(row[0]) == dishID:
            json_data['bitter'] = float(row[1])
            json_data['rich'] = float(row[2])
            json_data['salt'] = float(row[3])
            json_data['sour'] = float(row[4])
            json_data['sweet'] = float(row[5])
            json_data['umami'] = float(row[6])

    return json_data

def appendToReviewFile(dishIDs,userID,ratings,path):
    fields = [[str(dishIDs[i]), str(userID), str(ratings[i])] for i in range(len(dishIDs))]
    with open(path,'a',newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(fields)

def main():
    userID = eval(sys.argv[1])
    ratings = sys.argv[2]
    predictedDishes = sys.argv[3]
    predictedDishes = list(predictedDishes.split(','))
    ratings = [int(i) for i in ratings.split(',')]
    retVal = {}
    path = os.path.join(os.path.abspath(os.path.join(my_path, os.pardir)),'Team 3/review.csv')
    dishIDs = []
    for i in range(len(predictedDishes)):
        predictedDish = predictedDishes[i]
        rating = ratings[i]
        dishID, nutrientsData = getDocumentDetails(predictedDish)
        flavourData = flavourDetails(dishID)
        retVal[predictedDish] = {'nutrientsData': nutrientsData, 'flavourData': flavourData}
        dishIDs.append(dishID)

    appendToReviewFile(dishIDs,userID,ratings,path)
    print(retVal)

if __name__ == '__main__':
    
    main()
    sys.stdout.flush()
