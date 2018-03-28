from keras import Model
from keras.layers import Conv2D, MaxPool2D, BatchNormalization, Flatten, Dense, Input, ZeroPadding2D, Dropout, AveragePooling2D, Activation, concatenate


def inception_module(input_layer, filter_list, tag=''):
    if tag == '':
        arm_1 = Conv2D(filter_list[0], 1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
        arm_2 = Conv2D(filter_list[1], 1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
        arm_2 = Conv2D(filter_list[2], 3, strides=(1, 1), padding='same', activation='relu')(arm_2)
        arm_3 = Conv2D(filter_list[3], 1, strides=(1, 1), padding='valid', activation='relu')(input_layer)
        arm_3 = Conv2D(filter_list[4], 5, strides=(1, 1), padding='same', activation='relu')(arm_3)
        augmented_input_layer = ZeroPadding2D(padding=(1, 1))(input_layer)
        arm_4 = MaxPool2D((3, 3), (1, 1))(augmented_input_layer)
        arm_4 = Conv2D(filter_list[5], 1, strides=(1, 1), activation='relu')(arm_4)
        merged_vector = concatenate([arm_1, arm_2, arm_3, arm_4], axis=3)

    else:
        arm_1 = Conv2D(filter_list[0], 1, strides=(1, 1), padding='valid', activation='relu',
                       name=(tag + '_arm1_reduction'))(input_layer)
        arm_2 = Conv2D(filter_list[1], 1, strides=(1, 1), padding='valid', activation='relu',
                       name=(tag + '_arm2_reduction'))(input_layer)
        arm_2 = Conv2D(filter_list[2], 3, strides=(1, 1), padding='same', activation='relu',
                       name=(tag + '_arm2_conv'))(arm_2)
        arm_3 = Conv2D(filter_list[3], 1, strides=(1, 1), padding='valid', activation='relu',
                       name=(tag + '_arm3_reduction'))(input_layer)
        arm_3 = Conv2D(filter_list[4], 5, strides=(1, 1), padding='same', activation='relu',
                       name=(tag + '_arm3_conv'))(arm_3)
        augmented_input_layer = ZeroPadding2D(padding=(1, 1))(input_layer)
        arm_4 = MaxPool2D((3, 3), (1, 1), name=(tag + '_arm4_maxpool'))(augmented_input_layer)
        arm_4 = Conv2D(filter_list[5], 1, strides=(1, 1), activation='relu', name=(tag + '_arm4_conv'))(arm_4)
        merged_vector = concatenate([arm_1, arm_2, arm_3, arm_4], axis=3, name=(tag + '_merge'))

    return merged_vector


class inceptionv1:
    def __init__(self, categories =1000):
        img_shape = (224, 224, 3)
        main_input = Input(img_shape, name='main_input')
        augmented_input = ZeroPadding2D(padding=(3, 3))(main_input)

        layer_1 = Conv2D(64, 7, strides=(2, 2), padding='valid', activation='relu')(augmented_input)
        augmented_layer_1 = ZeroPadding2D(padding=(1, 1))(layer_1)
        layer_2 = MaxPool2D((3, 3), (2, 2))(augmented_layer_1)
        layer_3 = BatchNormalization()(layer_2)
        layer_4 = Conv2D(64, 1, strides=(1, 1), padding='same', activation='relu')(layer_3)
        layer_5 = Conv2D(192, 3, strides=(1, 1), padding='same', activation='relu')(layer_4)
        layer_6 = BatchNormalization()(layer_5)
        augmented_layer_6 = ZeroPadding2D(padding=(1, 1))(layer_6)
        layer_7 = MaxPool2D(3, (2, 2))(augmented_layer_6)

        layer_8 = inception_module(layer_7, [64, 96, 128, 16, 32, 32], tag='inception_1')
        layer_9 = inception_module(layer_8, [128, 128, 192, 32, 96, 64], tag='inception_2')
        augmented_layer_9 = ZeroPadding2D(padding=(1, 1))(layer_9)
        layer_10 = MaxPool2D((3, 3), (2, 2))(augmented_layer_9)
        layer_11 = inception_module(layer_10, [192, 96, 208, 16, 48, 64], tag='inception_3')

        # AUX Output 1
        layer_11a = AveragePooling2D((5, 5), strides=(3, 3))(layer_11)
        layer_11b = Conv2D(128, 1, strides=(1, 1), activation='relu')(layer_11a)
        layer_11c = Flatten()(layer_11b)
        layer_11d = Dense(1024, activation="relu")(layer_11c)
        layer_11e = Dense(categories, activation="softmax")(layer_11d)

        layer_12 = inception_module(layer_11, [160, 112, 224, 24, 64, 64], tag='inception_4')
        layer_13 = inception_module(layer_12, [128, 128, 256, 24, 64, 64], tag='inception_5')
        layer_14 = inception_module(layer_13, [112, 144, 288, 32, 64, 64], tag='inception_6')

        # AUX Output 2
        layer_14a = AveragePooling2D((5, 5), strides=(3, 3))(layer_14)
        layer_14b = Conv2D(128, 1, strides=(1, 1), activation='relu')(layer_14a)
        layer_14c = Flatten()(layer_14b)
        layer_14d = Dense(1024, activation="relu")(layer_14c)
        layer_14e = Dense(categories, activation="softmax")(layer_14d)

        layer_15 = inception_module(layer_14, [256, 160, 320, 32, 128, 128], tag='inception_7')
        augmented_layer_15 = ZeroPadding2D(padding=(1, 1))(layer_15)
        layer_16 = MaxPool2D((3, 3), (2, 2))(augmented_layer_15)
        layer_17 = inception_module(layer_16, [256, 160, 320, 32, 128, 128], tag='inception_8')
        layer_18 = inception_module(layer_17, [384, 192, 384, 48, 128, 128], tag='inception_9')
        layer_19 = AveragePooling2D((7, 7), (1, 1))(layer_18)
        flatten = Flatten()(layer_19)
        layer_20 = Dropout(0.4)(flatten)
        layer_21 = Dense(categories)(layer_20)
        layer_22 = Activation('softmax')(layer_21)

        self.model = Model(inputs=[main_input], outputs=[layer_22, layer_11e, layer_14e])

    def get_model(self):
        return self.model