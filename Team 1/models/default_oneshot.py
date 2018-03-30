from keras.layers import Conv2D, MaxPool2D, BatchNormalization, merge
from keras import Sequential
from keras import Model
from keras import Input
from keras import backend as K
from keras.regularizers import l2
import numpy.random as rng
from keras.layers import Flatten, Dense


def w_init(shape, name=None):
    values = rng.normal(loc=0, scale=1e-2, size=shape)
    return K.variable(values, name=name)


def b_init(shape, name=None):
    values = rng.normal(loc=0.5, scale=1e-2, size=shape)
    return K.variable(values, name=name)


class default_oneshot():
    def __init__(self, dimensions):
        img_shape = tuple(dimensions)
        left_input = Input(img_shape, name='left_input')
        right_input = Input(img_shape, name='right_input')

        model = Sequential()
        model.add(Conv2D(filters=10, kernel_size=5, padding='same', activation='relu', kernel_regularizer=l2(2e-4), kernel_initializer='random_normal', bias_initializer='random_normal', input_shape=[224, 224, 3]))
        model.add(MaxPool2D())
        model.add(BatchNormalization())
        model.add(Conv2D(filters=20, kernel_size=5, padding='same', kernel_regularizer=l2(2e-4), kernel_initializer='random_normal', bias_initializer='random_normal', activation='relu'))
        model.add(MaxPool2D(pool_size=(4, 4)))
        model.add(BatchNormalization())
        model.add(Conv2D(filters=40, kernel_size=5, padding='same', kernel_regularizer=l2(2e-4), kernel_initializer='random_normal', bias_initializer='random_normal', activation='relu'))
        model.add(MaxPool2D(pool_size=(4, 4)))
        model.add(BatchNormalization())
        model.add(Flatten())
        model.add(Dense(320, activation='sigmoid', kernel_regularizer=l2(1e-3), kernel_initializer='random_normal', bias_initializer='random_normal'))

        encoding_left = model(left_input)
        encoding_right = model(right_input)
        distance = lambda x: K.abs((x[0] - x[1]) ** 2)
        merged_vector = merge(inputs=[encoding_left, encoding_right], mode=distance, output_shape=lambda x: x[0])
        predict_layer = Dense(1, activation='sigmoid', name='main_output')(merged_vector)
        siamese_network = Model(inputs=[left_input, right_input], outputs=predict_layer)

        self.model = siamese_network

    def get_model(self):
        return self.model
