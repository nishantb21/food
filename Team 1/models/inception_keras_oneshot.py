from keras.applications import InceptionV3
from keras import Model, Input
from keras import backend as K
from keras.layers import merge, Dense, Flatten


class inception_keras_oneshot():
    def __init__(self, dimensions):
        img_shape = tuple(dimensions)
        left_input = Input(img_shape, name='left_input')
        right_input = Input(img_shape, name='right_input')

        model = InceptionV3(include_top=False)
        model_augmented = Model(inputs=[model.input], outputs=[model.output])

        encoding_left = Flatten(name='flattened_left_input')(model_augmented(left_input))
        encoding_right = Flatten(name='flattened_right_input')(model_augmented(right_input))
        distance = lambda x: K.abs((x[0] - x[1]) ** 2)
        merged_vector = merge(inputs=[encoding_left, encoding_right], mode=distance, output_shape=lambda x: x[0])
        predict_layer = Dense(1, activation='sigmoid', name='main_output')(merged_vector)
        siamese_network = Model(inputs=[left_input, right_input], outputs=predict_layer)

        self.model = siamese_network

    def get_model(self):
        return self.model


if __name__ == '__main__':
    obj = inception_keras_oneshot([224, 224, 3])
    print(obj.get_model().summary())
