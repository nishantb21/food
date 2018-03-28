from .base_models import alexnet
from keras import Model, Input
from keras import backend as K
from keras.layers import merge, Dense


class alexnet_oneshot():
    def __init__(self, dimensions):
        img_shape = tuple(dimensions)
        left_input = Input(img_shape, name='left_input')
        right_input = Input(img_shape, name='right_input')

        model = alexnet(dimensions).get_model()
        model_augmented = Model(inputs=[model.input], outputs=[model.get_layer('flattened').output])

        encoding_left = model_augmented(left_input)
        encoding_right = model_augmented(right_input)
        distance = lambda x: K.abs((x[0] - x[1]) ** 2)
        merged_vector = merge(inputs=[encoding_left, encoding_right], mode=distance, output_shape=lambda x: x[0])
        predict_layer = Dense(1, activation='sigmoid', name='main_output')(merged_vector)
        siamese_network = Model(inputs=[left_input, right_input], outputs=predict_layer)

        self.model = siamese_network

    def get_model(self):
        return self.model


if __name__ == '__main__':
    obj = alexnet_oneshot([224, 224, 3])
    print(obj.get_model().summary())