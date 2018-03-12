import os
import csv
import sys
from pymongo import MongoClient

my_path = os.path.abspath(os.path.dirname(__file__))

def main(userID):
    history = dict()
    userID = int(userID)
    c = MongoClient()
    db = c.foodDatabase
    collection = db.itemDetails

    reviewList = list(csv.reader(open(os.path.join(os.path.join(my_path, os.pardir),'Team 2/review.csv'))))

    for i in reviewList[-(len(reviewList)-1):]:
        if int(i[1]) == userID:
            document = collection.find_one({'dish_id':int(i[0])})
            history[document['dish_name']] = int(i[2])
    
    print(history)

if __name__ == "__main__":

    main(sys.argv[1])
    sys.stdout.flush()
