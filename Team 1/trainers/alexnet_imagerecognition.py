from keras import optimizers
from keras.callbacks import ReduceLROnPlateau
from models.base_models import alexnet
from dataset_loader import imagerecognition
from keras.preprocessing.image import ImageDataGenerator
from common import save_model, load_model
import numpy as np


def main(dataset_path, working_dir, testing_path, testing_working_dir, dimensions, batch_size, number_classes, epochs):
    def generator_augmented():
        while True:
            while not dataset_loader.done():
                x, y = dataset_loader.get_training_batch()
                gen = datagen.flow(x, y, batch_size=batch_size)
                x_augmented, y_augmented = next(gen)
                yield np.concatenate((x, x_augmented), axis=0), np.concatenate((y, y_augmented), axis=0)
            dataset_loader.reset()

    def generator():
        while True:
            while not dataset_loader.done():
                x, y = dataset_loader.get_training_batch()
                yield x, y
            dataset_loader.reset()

    # model = alexnet(dimensions, number_classes).get_model()
    model = load_model()
    reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=5, min_lr=0.001)
    sgd_optimizer = optimizers.SGD(lr=0.01, momentum=0.9, decay=0.0005)
    dataset_loader = imagerecognition.dataset_loader(dataset_path, working_dir, dimensions, batch_size)
    datagen = ImageDataGenerator(rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, horizontal_flip=True, vertical_flip=True)

    model.compile(sgd_optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit_generator(generator(), steps_per_epoch=dataset_loader.length / batch_size, epochs=epochs, callbacks=[reduce_lr])
    dataset_loader.delete_from_disk()
    save_model(model)

    dataset_loader = imagerecognition.dataset_loader(testing_path, testing_working_dir, dimensions, batch_size)
    print('Testing...')
    consolidated_images, consolidated_labels = dataset_loader.get_training_batch()
    while not dataset_loader.done():
        temp_images, temp_labels = dataset_loader.get_training_batch()
        consolidated_images = np.concatenate((consolidated_images, temp_images), axis=0)
        consolidated_labels = np.concatenate((consolidated_labels, temp_labels), axis=0)
    print(model.evaluate(consolidated_images, consolidated_labels))
    dataset_loader.delete_from_disk()


if __name__=="__main__":
    dataset_path = 'D:\\Python Projects\\8th Sem Project Work\\Resources\\food-101\\train'
    working_dir = "."
    testing_path = 'D:\\Python Projects\\8th Sem Project Work\\Resources\\food-101\\test'
    testing_working_dir = '.'
    batch_size = 128
    dimensions = [224, 224, 3]
    number_classes = 101
    epochs = 20

    main(dataset_path, working_dir, testing_path, testing_working_dir, dimensions, batch_size, number_classes, epochs)
