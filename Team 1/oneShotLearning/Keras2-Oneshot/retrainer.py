import util
import sys
import uuid
from pymongo import MongoClient
import json
from keras import Model
from keras.models import model_from_json
from keras.optimizers import Adam
# correctLabel = sys.argv[1]
# orgPath = sys.argv[2]
# destPath = '/home/unagi/IndianFoodRecognition/oneShotLearning/Dataset/Food Images/Train/'+correctLabel+str(uuid.uuid4())+'.jpg'
def loadModel():
    json_file = open('/home/unagi/phood/Team 1/oneShotLearning/Keras2-Oneshot/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("/home/unagi/phood/Team 1/oneShotLearning/Keras2-Oneshot/model.h5")
    # print("Loaded model from disk")
    return loaded_model
def saveModel(modelToSave):
    model_json = modelToSave.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    modelToSave.save_weights("model.h5")
    print("Saved model to disk")
path = '/home/unagi/phood/Team 1/oneShotLearning/Dataset/Food Images/Train'
c = MongoClient()
db = c.INDIANFOOD101
collection = db.retrainQueue
cursor = collection.find({})
image_label_pair = []
for document in cursor:
    temp = []
    correctLabel = document['CorrectLabel']
    orgPath = document['imgPath']
    print(orgPath)
    destPath = '/home/unagi/phood/Team 1/oneShotLearning/Dataset/Food Images/Train/'+correctLabel+'/'+str(uuid.uuid4())+'.jpg'
    print(destPath)
    temp.append(orgPath)
    temp.append(destPath)
    image_label_pair.append(temp)
# print(collection.delete_many({}))
dataset = util.dataset_loader(path, (128, 128, 1))
left_inputs, right_inputs, labels = dataset.update_dataset(image_label_pair)
model = loadModel()
optimizer = Adam(0.00006)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
model.fit({'left_input': left_inputs, 'right_input': right_inputs}, {'main_output': labels}, epochs=10, verbose=1, validation_split=0.2)
saveModel(model)
print("Model Retrained")
sys.stdout.flush()
