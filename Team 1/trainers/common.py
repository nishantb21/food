import os
from keras.models import model_from_json

def save_model(model_to_save):
    model_json = model_to_save.to_json()
    with open(os.path.abspath("model.json"), "w") as json_file:
        json_file.write(model_json)
    model_to_save.save_weights("model.h5")
    print("Saved model to disk")


def load_model():
    json_file = open(os.path.abspath('model.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")
    return loaded_model