from pymongo import MongoClient
import json

def insertData(collection, data):
    collection.insert_many(data)

def main():

    c = MongoClient()
    db = c.foodDatabase
    collection = db.itemDetails

    with open('database.json', 'r') as infile:
        documents = json.load(infile)
        insertData(collection, documents)

if __name__ == "__main__":
    main()