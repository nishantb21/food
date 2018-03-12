from pymongo import MongoClient
import json

def normalizeNurtitionFields(data):
    if type(data) == list:
        quantity = data[0]
        quantity = ''.join(quantity.split(" "))

        percentage = data[1]
        percentage = ''.join(percentage.split(" "))

        if (percentage[len(percentage) - 2] == '%' and percentage[len(percentage) - 1] == '%'):
            percentage = percentage[0:- 1]

        return [quantity, percentage]
    else:
        return None

def normalizeNameFields(data):
    return data.lower()

def constructData(ids, collection):
    documents = []
    actual_keys = []
    mapping = {}

    for dishId in ids:
        
        document = collection.find_one({'dish_id':dishId})
        del document['_id']
        for key in document['nutrients']:
            if key not in actual_keys:
                actual_keys.append(key)
                mapping[key] = key.lower()

        documents.append(document)

    actual_keys = set([ x.lower() for x in actual_keys])
    return documents, actual_keys, mapping

def cleanData(documents, actual_keys, mapping):
    for document in documents:

        document['dish_name'] = normalizeNameFields(document['dish_name'])

        if document['nutrients'] == {}:
            pass
        else:
            tempNutrients = {}
            for key in actual_keys:
                tempNutrients[key] = None
            
            for key in document['nutrients']:
                tempNutrients[mapping[key]] = normalizeNurtitionFields(document['nutrients'][key])

            document['nutrients'] = tempNutrients

    return documents

def main():

    totalDishes = 1381
    ids = list(range(1, totalDishes + 1))
    c = MongoClient()
    db = c.INDIANFOOD101
    collection = db.itemDetails2

    documents, actual_keys, mapping = constructData(ids, collection)
    augmented_documents = cleanData(documents, actual_keys, mapping)

    print(augmented_documents)

if __name__ == "__main__":
    main()