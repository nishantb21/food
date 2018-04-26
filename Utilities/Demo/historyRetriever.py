import os
import csv
import sys
from pymongo import MongoClient

my_path = os.path.abspath(os.path.dirname(__file__))

def main(userID):
    data = dict()
    history = dict()
    userData = dict()
    userID = int(userID)
    c = MongoClient()
    db = c.foodDatabase
    collection = db.itemDetails

    reviewList = list(csv.reader(open(os.path.join(os.path.join(my_path, os.pardir),'Team 3/review.csv'))))

    for i in reviewList[-(len(reviewList)-1):]:
        if int(i[1]) == userID:
            document = collection.find_one({'dish_id':int(i[0])})
            history[document['dish_name']] = int(i[2])

    userDataList = list(csv.reader(open(os.path.join(os.path.join(my_path, os.pardir),'Team 3/user_profile.csv'))))
    
    for i in userDataList[1:]:
        if int(i[0]) == userID:
            if i[1] == 'm':
                userData['gender'] = 'Male'
            else:
                userData['gender'] = 'Female'
            userData['age'] = int(i[2])
            userData['height'] = i[3] + ' cms'
            userData['weight'] = i[4] + ' kgs'
            userData['condition'] = i[5]
            userData['bmratio'] = float(i[6])
            if i[7] == '0':
                userData['vegnonveg'] = 'Veg'
            else:
                userData['vegnonveg'] = 'Non-Veg'
            break

    userData["allergies"] = []
    userAllergiesList = list(csv.reader(open(os.path.join(os.path.join(my_path, os.pardir),'Team 3/user_allergies.csv'))))
    for i in userAllergiesList[1:]:
        if int(i[0]) == userID:
            userData["allergies"].append(i[1])

    data['history'] = history
    data['userData'] = userData
    print(data)


if __name__ == "__main__":

    main(sys.argv[1])
    sys.stdout.flush()
