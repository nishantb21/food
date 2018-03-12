import os
import urllib.request
import requests
import json
endpoint = 'https://api.yummly.com/v1/api/recipes'
APP_ID = '052a0d74'
APP_KEY = '813cc9aa71c024c1b98dacf7b428d77b'
path = '/home/unagi/IndianFoodRecognition/oneShotLearning/Dataset/Train'
resp_json = []
for subdir,dir,files in os.walk(path):
    if len(files)>0:
        dish = subdir.split('/')[-1]
        print(dish)
        params = {
        '_app_id':APP_ID,
        '_app_key':APP_KEY,
        'q':dish,
        'requirePictures':'true'
        }
        try:
            r = requests.get(endpoint,params=params)
            resp_json.append(json.loads(r.text))
        except requests.exceptions.RequestException as e:
            print(e)
with open('yummlyResults.json','w') as outfile:
    json.dump(resp_json,outfile)
