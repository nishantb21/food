from models import alexnet_oneshot
from dataset_loader import oneshot
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt
import json
from scipy import misc
import numpy as np
from keras.models import model_from_json
from common import save_model, load_model


def main(dataset_path, working_dir, testing_path, testing_working_dir, dimensions, batch_size, epochs):
    def generator_augmented():
        datagen = ImageDataGenerator(rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, horizontal_flip=True, vertical_flip=True)
        while True:
            while not dataset_loader.done():
                x, y, z = dataset_loader.get_training_batch()
                gen = datagen.flow(x, y, batch_size=batch_size)
                x_augmented, y_augmented = next(gen)
                yield ({'left_input': np.concatenate((x, x_augmented), axis=0), 'right_input': np.concatenate((y, y_augmented), axis=0)}, {'main_output': np.concatenate((z, z), axis=0)})
            dataset_loader.reset()

    def generator():
        while True:
            while not dataset_loader.done():
                x, y, z = dataset_loader.get_training_batch()
                yield ({'left_input': x, 'right_input': y},  {'main_output': z})
            dataset_loader.reset()

    model = alexnet_oneshot(dimensions).get_model()
    optimizer = Adam(0.00006)
    dataset_loader = oneshot.dataset_loader(dataset_path, working_dir, dimensions, batch_size)

    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    model.fit_generator(generator(), steps_per_epoch=dataset_loader.length//batch_size, epochs=epochs)
    dataset_loader.delete_from_disk()
    save_model(model)

    dataset_loader = oneshot.dataset_loader(testing_path, testing_working_dir, dimensions, batch_size)
    consolidated_left, consolidated_right, consolidated_label = dataset_loader.get_training_batch()
    while not dataset_loader.done():
        left, right, label = dataset_loader.get_training_batch()
        consolidated_left = np.concatenate((consolidated_left, left), axis=0)
        consolidated_right = np.concatenate((consolidated_right, right), axis=0)
        consolidated_label = np.concatenate((consolidated_label, label), axis=0)

    print("Testing...")
    print(model.evaluate(x={'left_input': consolidated_left, 'right_input': consolidated_right}, y=consolidated_label))
    dataset_loader.delete_from_disk()


if __name__=='__main__':
    dataset_path = 'D:\\Python Projects\\8th Sem Project Work\\Resources\\imageData43scaled\\Train'
    working_dir = '.'
    testing_path = 'D:\\Python Projects\\8th Sem Project Work\\Resources\\imageData43scaled\\Test'
    testing_working_dir = '.'
    dimensions = [224, 224, 3]
    batch_size = 32
    epochs = 1
    main(dataset_path, working_dir, testing_path, testing_working_dir, dimensions, batch_size, epochs)