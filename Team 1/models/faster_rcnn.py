from base_models import alexnet
from keras import Model, Input
from keras import backend as K
from keras.layers import merge, Dense, Conv2D


def rpn_layer(feature_map, anchors=9, backend='alexnet'):
    number_filters = 256
    intermediate = Conv2D(filters=number_filters, kernel_size=3, padding='same', activation='relu', kernel_initializer='normal', name='rpn_conv1')(feature_map)
    classes = Conv2D(filters=anchors, kernel_size=1, activation='sigmoid', kernel_initializer='uniform', name='rpn_out_class')(intermediate)
    regression_boxes = Conv2D(filters=(4 * anchors), kernel_size=1, activation='linear', kernel_initializer='zero', name='rpn_out_regress')(intermediate)

    return classes, regression_boxes


class faster_rcnn():
    def __init__(self, dimensions, backend='alexnet'):
        img_shape = tuple(dimensions)
        main_input = Input(img_shape, name='main_input')
        if backend == 'alexnet':
            model = alexnet(dimensions).get_model()
        else:
            raise ValueError('Backend Invalid.')

        model_augmented = Model(inputs=[model.input], outputs=[model.get_layer('conv2d_5').output])
        feature_map = model_augmented(main_input)
        classes, regression_boxes = rpn_layer(feature_map)
        rpn_network = Model(inputs=main_input, outputs=[classes, regression_boxes])

        self.model = rpn_network

    def get_model(self):
        return self.model


if __name__ == '__main__':
    dimensions = [448, 448, 3]
    obj = faster_rcnn(dimensions)
    print(obj.get_model().summary())