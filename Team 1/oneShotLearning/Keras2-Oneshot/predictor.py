from keras.layers import Conv2D, MaxPool2D, BatchNormalization, Dense, Flatten, merge
from keras.optimizers import Adam
from keras import Sequential
from keras import Model
from keras.models import model_from_json
from keras import Input
from keras import backend
from keras.regularizers import l2
import numpy as np
from scipy import misc
import numpy.random as rng
import os
import uuid
import json
import sys
my_path = os.path.abspath(os.path.dirname(__file__))
def loadModel():
    json_file = open(os.path.join(my_path,'model.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(os.path.join(my_path,"model.h5"))
    # print("Loaded model from disk")
    return loaded_model

def predict(PredPath):
    img_shape = (128,128,3)
    CatPath = os.path.join(my_path,'../Dataset/Food Images/Train')
    siamese_network = loadModel()
    generalSelections = []
    predictionImage = []
    labels = []
    categories = 0
    for subdir,dir,files in os.walk(CatPath):
        categories += len(dir)
        if len(files)>2:
            imgPath = os.path.join(subdir,files[0])
            labels.append(subdir.split('/')[-1])
            img = misc.imread(imgPath)
            img = np.reshape(misc.imresize(img, img_shape), img_shape)
            generalSelections.append(img)
    predImg = misc.imread(PredPath)
    predImg = np.reshape(misc.imresize(predImg, img_shape), img_shape)
    predictionImage = [predImg] * categories
    preds = siamese_network.predict({'left_input': np.array(generalSelections),'right_input': np.array(predictionImage)})
    predDict = {}
    for i in range(len(preds)):
        predDict[str(labels[i])] = float("{0:.3f}".format(float(preds[i])*100.0))
    d = [(k,v) for k,v in predDict.items()]
    print(dict(sorted(d, key=lambda x: x[1], reverse=True)[:5]))
        # print(k,v)
    with open(os.path.join(my_path,'predictions/predictions.json'),'w') as outfile:
        json.dump(predDict, outfile)
    # for k,v in sorted(predDict.items()):
    #     print(k,v)
    # checkCorrectness(PredPath,CatPath)
predict(sys.argv[1])
sys.stdout.flush()
