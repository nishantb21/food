import requests
import json
import os
import urllib.request
import uuid
'''Google custom search api - 100 calls per day'''
API_KEY = 'AIzaSyAgNT8qFPr-wAak1dUY0DoPArYxTXP1jnE'
search_Engine_ID = '018112325597161025444:rdzoa-kiouy'
base_url = 'https://www.googleapis.com/customsearch/v1'
# %%
def getDishNames():
    d = json.load(open('/home/unagi/IndianFoodRecognition/oneShotLearning/Dataset/itemdetails.json'))
    return [i['dish_name'] for i in d]

def dirExists(dish):
    if os.path.exists(dish):
        return True
    return False
def createDishDir(dish):
    os.makedirs(dish)
def populateDishDir(dish,link,counter):
    urllib.request.urlretrieve(link,dish+'/'+str(counter)+'.jpg')
def collectImages(path):
    dishes = getDishNames()
    params = {}
    reqCount = 0
    for dish in dishes:
        if reqCount!=25:
            print(dish)
            if not dirExists(path+dish):
                createDishDir(path+dish)
                if 'Train' in path:
                    params = {
                    'key':API_KEY,
                    'cx':search_Engine_ID,
                    'q':dish,
                    'searchType':'image'
                    }
                else:
                    params = {
                    'key':API_KEY,
                    'cx':search_Engine_ID,
                    'q':dish,
                    'searchType':'image',
                    'start':'10'
                    }
                r = requests.get(base_url,params=params)
                reqCount += 1
                try:
                    print(r.text)
                    resp_json = json.loads(r.text)
                except requests.exceptions.RequestException as e:
                    print(e)
                counter = 0
                for i in resp_json['items']:
                    try:
                        counter += 1
                        print(i['link'])
                        populateDishDir(path+dish,i['link'],counter)
                    except:
                        print('encountered an error, continuing')
                        continue
def fillUp(path):
    for subdir,dir,files in os.walk(path):
        if len(files) > 0 and len(files) < 10:
            remaining = 10-len(files)
            dish = subdir.split('/')[-1]
            params = {
            'key':API_KEY,
            'cx':search_Engine_ID,
            'q':dish,
            'searchType':'image',
            'start':'10',
            'num':remaining
            }
            r = requests.get(base_url,params=params)
            try:
                resp_json = json.loads(r.text)
            except request.exceptions.RequestException as e:
                print(e)
            for i in resp_json['items']:
                try:
                    print(i['link'])
                    populateDishDir(path+dish,i['link'],uuid.uuid4())
                except:
                    print('encountered an error,continuing')
                    continue
def main():
    # collectImages('Food Images/Train/')
    # collectImages('Food Images/Test/')
    fillUp('Food Images/Train/')
    # fillUp('Food Images/Test/')

if __name__ == '__main__':
    main()
