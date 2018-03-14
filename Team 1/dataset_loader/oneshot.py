import os
import h5py
import numpy as np
from scipy import misc
import itertools
import random
import json
import sys
import time

class dataset_loader:
    dimensions = ()
    path = ''
    image_pairs_left = []
    image_pairs_right = []
    image_pairs_labels = []
    categories = []
    images_paths = {}
    default_name = 'dataset_oneshot.json'
    cache = []
    cache_mapping = {}
    batch_size = 0
    length = 0
    current_count = 0

    def __init__(self, dataset_path, working_path, dimensions, batch_size):

        dataset_path = os.path.abspath(dataset_path)
        working_path = os.path.abspath(working_path)

        files = [x for x in os.listdir(working_path) if os.path.isfile(os.path.join(working_path, x))]
        self.path = working_path

        if self.default_name in files:
            print("Reading from cache...")
            self.load_from_disk()
        else:
            print("Reading afresh...")
            self.categories = [x for x in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, x))]
            self.dimensions = dimensions
            self.batch_size = batch_size
            for category in self.categories:
                temp_path = os.path.join(dataset_path, category)
                temp_category_paths = os.listdir(temp_path)
                temp_category_paths = [os.path.join(temp_path, x) for x in temp_category_paths]
                self.images_paths[category] = temp_category_paths

            self.generate_dataset()
            self.save_to_disk()

    def delete_from_disk(self):
        os.remove(os.path.join(self.path, self.default_name))

    def load_from_disk(self):
        path = os.path.join(self.path, self.default_name)
        with open(path, 'r') as jfl:
            data = json.load(jfl)
            self.image_pairs_left = data['image_pairs_left']
            self.image_pairs_right = data['image_pairs_right']
            self.image_pairs_labels = data['image_pairs_labels']
            self.categories = data['categories']
            self.dimensions = tuple(data['dimensions'])
            self.images_paths = data['images_paths']
            self.batch_size = data['batch_size']
            self.length = data['length']
            self.current_count = data['current_count']

    def save_to_disk(self):
        path = os.path.join(self.path, self.default_name)
        json_to_write = dict()
        json_to_write['image_pairs_left'] = self.image_pairs_left
        json_to_write['image_pairs_right'] = self.image_pairs_right
        json_to_write['image_pairs_labels'] = self.image_pairs_labels
        json_to_write['categories'] = self.categories
        json_to_write['dimensions'] = list(self.dimensions)
        json_to_write['images_paths'] = self.images_paths
        json_to_write['batch_size'] = self.batch_size
        json_to_write['length'] = self.length
        json_to_write['current_count'] = self.current_count

        with open(path, 'w') as jfl:
            json.dump(json_to_write, jfl, sort_keys=True, indent=4)

    def done(self):
        return self.length == self.current_count

    def reset(self):
        self.current_count = 0

    def read_images(self, paths):
        ret_val = []
        for path in paths:
            if path in self.cache_mapping.keys():
                img = self.cache[self.cache_mapping[path]]
            else:
                img = misc.imread(path)
                img = np.reshape(misc.imresize(img, self.dimensions), self.dimensions)
                self.cache_mapping[path] = len(self.cache)
                self.cache.append(img)
            ret_val.append(img)

        return np.asarray(ret_val)

    def generate_dataset(self):
        for category in self.categories:
            same_category_combinations = list(itertools.combinations(self.images_paths[category], 2))
            no_positive_examples = len(same_category_combinations)
            for combination in same_category_combinations:
                self.image_pairs_left.append(combination[0])
                self.image_pairs_right.append(combination[1])
                self.image_pairs_labels.append(1)
            self.length += no_positive_examples

            other_categories = [x for x in self.categories if(x != category)]
            for other_category in other_categories:
                different_category_combinations = list(itertools.product(self.images_paths[category], self.images_paths[other_category]))
                temp_length = min(no_positive_examples, len(different_category_combinations))
                different_category_combinations = random.sample(different_category_combinations, temp_length)
                for combination in different_category_combinations:
                    self.image_pairs_left.append(combination[0])
                    self.image_pairs_right.append(combination[1])
                    self.image_pairs_labels.append(0)
                self.length += temp_length

    def update_dataset(self, image_label_pair):
        # image_label_pair --> [[path of image,name of category],[path...,category],...]
        return_image_pairs_left = []
        return_image_pairs_right = []
        return_image_pairs_labels = []
        for pair in image_label_pair:
            image_path = os.path.abspath(pair[0])
            category = pair[1]

            same_category_combinations = list(itertools.product(self.images_paths[category], [image_path]))
            additional_positive_length = len(same_category_combinations)
            for combination in same_category_combinations:
                return_image_pairs_left.append(combination[0])
                return_image_pairs_right.append(combination[1])
                return_image_pairs_labels.append(1)
            self.length += additional_positive_length

            other_categories = [x for x in self.categories if (x != category)]
            for other_category in other_categories:
                different_category_combinations = list(itertools.product(self.images_paths[other_category], [image_path]))
                temp_length = min(additional_positive_length, len(different_category_combinations))
                different_category_combinations = random.sample(different_category_combinations, temp_length)
                for combination in different_category_combinations:
                    return_image_pairs_left.append(combination[0])
                    return_image_pairs_right.append(combination[1])
                    return_image_pairs_labels.append(0)
                self.length += temp_length

        self.image_pairs_left.extend(return_image_pairs_left)
        self.image_pairs_right.extend(return_image_pairs_right)
        self.image_pairs_labels.extend(return_image_pairs_labels)

    def update_categories(self, new_categories):
        pass

    def get_training_batch(self):
        start_index = self.current_count
        end_index = min(start_index + self.batch_size, self.length)
        self.current_count = end_index
        return self.read_images(self.image_pairs_left[start_index:end_index]), self.read_images(self.image_pairs_right[start_index:end_index]), np.asarray(self.image_pairs_labels[start_index:end_index])


if __name__ == '__main__':
    t1 = time.time()
    obj = dataset_loader('D:\\Python Projects\\8th Sem Project Work\\Resources\\FoodDataset\\Train', '.', [224, 224, 3], 32)

    while not obj.done():
        a, b, c = obj.get_training_batch()
        print(a.shape)
        print(b.shape)
        print(c.shape)

    t2 = time.time()
    print("Time taken:", t2 - t1)