from keras import Model
from keras.layers import Conv2D, MaxPool2D, BatchNormalization, Flatten, Dense, Input, ZeroPadding2D, Dropout
from keras.initializers import RandomNormal, Zeros, Ones


class alexnet:
    def __init__(self, dimensions, categories =1000):
        img_shape = tuple(dimensions)
        number_classes = categories

        initializer = RandomNormal(mean=0.0, stddev=0.01)
        zero_initializer = Zeros()
        one_initializer = Ones()
        main_input = Input(img_shape, name='main_input')
        main_input_padded = ZeroPadding2D(padding=(3, 3), name='main_input_padded')(main_input)
        conv2d_1 = Conv2D(filters=96, kernel_size=11, strides=(4, 4), padding='valid', bias_initializer=zero_initializer, kernel_initializer=initializer, activation='relu', name='conv2d_1')(main_input_padded)
        maxpool_1 = MaxPool2D(pool_size=(3, 3), strides=(2, 2), name='maxpool_1')(conv2d_1)
        norm_1 = BatchNormalization(name='norm_1')(maxpool_1)
        conv2d_2 = Conv2D(filters=256, kernel_size=5, strides=(1, 1), padding='same', bias_initializer=one_initializer, kernel_initializer=initializer, activation='relu', name='conv2d_2')(norm_1)
        maxpool_2 = MaxPool2D(pool_size=(3, 3), strides=(2, 2), name='maxpool_2')(conv2d_2)
        norm_2 = BatchNormalization(name='norm_2')(maxpool_2)
        conv2d_3 = Conv2D(filters=384, kernel_size=3, strides=(1, 1), padding='same', bias_initializer=zero_initializer, kernel_initializer=initializer, activation='relu', name='conv2d_3')(norm_2)
        conv2d_4 = Conv2D(filters=384, kernel_size=3, strides=(1, 1), padding='same', bias_initializer=one_initializer, kernel_initializer=initializer, activation='relu', name='conv2d_4')(conv2d_3)
        conv2d_5 = Conv2D(filters=256, kernel_size=3, strides=(1, 1), padding='same', bias_initializer=one_initializer, kernel_initializer=initializer, activation='relu', name='conv2d_5')(conv2d_4)
        maxpool_3 = MaxPool2D(pool_size=(3, 3), strides=(2, 2), name='maxpool_3')(conv2d_5)
        flattened = Flatten(name='flattened')(maxpool_3)
        dense_1 = Dense(units=4096, bias_initializer=zero_initializer, kernel_initializer=initializer, activation='relu', name='dense_1')(flattened)
        dropout_1 = Dropout(0.5, name='dropout_1')(dense_1)
        dense_2 = Dense(units=4096, bias_initializer=zero_initializer, kernel_initializer=initializer, activation='relu', name='dense_2')(dropout_1)
        dropout_2 = Dropout(0.5, name='dropout_2')(dense_2)
        classification = Dense(units=number_classes, activation='softmax', name='classification')(dropout_2)

        self.model = Model(inputs=[main_input], outputs=[classification])

    def get_model(self):
        return self.model


if __name__ == '__main__':
    obj = alexnet().get_model()
    obj.summary()