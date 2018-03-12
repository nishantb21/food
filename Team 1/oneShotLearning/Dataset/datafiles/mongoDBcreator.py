from pymongo import MongoClient
import json
itemDetails = '/home/unagi/IndianFoodRecognition/oneShotLearning/Dataset/datafiles/datafiles/itemDetails2.json'

def readJsonFile(path):
    c = MongoClient()
    db = c.INDIANFOOD101
    collection = db.itemDetails2
    documents = []
    with open(path) as inFile:
        parser = json.load(inFile)
        for i in parser[:50]:
            documents.append(i)
        print(len(documents))
        result = collection.insert_many(documents)
if __name__ == '__main__':
    readJsonFile(itemDetails)
