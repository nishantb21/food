from pymongo import MongoClient
import json
import os
my_path = os.path.abspath(os.path.dirname(__file__))
itemDetails = os.path.join(my_path,'itemdetails.json')

def readJsonFile(path):
    c = MongoClient()
    db = c.INDIANFOOD101
    collection = db.itemDetails2
    documents = []
    with open(path) as inFile:
        parser = json.load(inFile)
        for i in parser:
            documents.append(i)
        print(len(documents))
        result = collection.insert_many(documents)
if __name__ == '__main__':
    readJsonFile(itemDetails)
