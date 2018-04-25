import os
import numpy as np
import cv2
import json
import sys
import time

bad_counter = 0
class dataset_loader:
    dimensions = ()
    working_path = ''
    dataset_path = ''
    categories = []
    images_paths = []
    labels = []
    default_name = 'dataset_imagerecognition.json'
    number_categories = 0
    batch_size = 0
    length = 0
    current_count = 0

    def __init__(self, dataset_path, working_path, dimensions, batch_size):

        dataset_path = os.path.abspath(dataset_path)
        working_path = os.path.abspath(working_path)

        files = [x for x in os.listdir(working_path) if os.path.isfile(os.path.join(working_path, x))]
        self.working_path = working_path
        self.dataset_path = dataset_path

        if self.default_name in files:
            print("Reading from cache...")
            self.load_from_disk()
        else:
            print("Reading afresh...")
            self.categories = [x for x in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, x))]
            self.dimensions = tuple(dimensions)
            self.batch_size = batch_size
            self.generate_dataset()
            self.save_to_disk()

    def delete_from_disk(self):
        os.remove(os.path.join(self.working_path, self.default_name))

    def load_from_disk(self):
        path = os.path.join(self.working_path, self.default_name)
        with open(path, 'r') as jfl:
            data = json.load(jfl)
            self.images_paths = data['images_paths']
            self.labels = data['labels']
            self.number_categories = data['number_categories']
            self.dataset_path = data['dataset_path']
            self.working_path = data['working_path']
            self.categories = data['categories']
            self.dimensions = tuple(data['dimensions'])
            self.batch_size = data['batch_size']
            self.length = data['length']
            self.current_count = data['current_count']

    def save_to_disk(self):
        path = os.path.join(self.working_path, self.default_name)
        json_to_write = dict()
        json_to_write['images_paths'] = self.images_paths
        json_to_write['labels'] = self.labels
        json_to_write['number_categories'] = self.number_categories
        json_to_write['dataset_path'] = self.dataset_path
        json_to_write['working_path'] = self.working_path
        json_to_write['categories'] = self.categories
        json_to_write['dimensions'] = list(self.dimensions)
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
            try:
                if self.dimensions[2] == 3:
                    img = cv2.imread(path, cv2.IMREAD_COLOR)
                else:
                    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (self.dimensions[0], self.dimensions[1]))
                ret_val.append(np.reshape(img, self.dimensions))
            except Exception as e:
                global bad_counter
                bad_counter += 1

        return np.asarray(ret_val)

    def shuffle_dataset(self):
        current_indices = [0] * self.number_categories
        count = 0
        for i in range(self.length):
            current_category = self.categories[count]
            label = [0] * self.number_categories
            label[count] = 1
            self.images_paths.append(self.images_paths_mapping[current_category][current_indices[count]])
            self.labels.append(label)

            current_indices[count] += 1
            count += 1
            count = count % self.number_categories
            if i != (self.length - 1):
                while current_indices[count] == self.categories_length[count]:
                    count += 1
                    count = count % self.number_categories

        del self.images_paths_mapping
        del self.categories_length

    def generate_dataset(self):
        self.number_categories = len(self.categories)
        self.images_paths_mapping = {}
        self.categories_length = []
        for category in self.categories:
            temp_path = os.path.join(self.dataset_path, category)
            temp_category_paths = os.listdir(temp_path)
            temp_category_paths = [os.path.join(temp_path, x) for x in temp_category_paths]
            paths_length = len(temp_category_paths)
            self.images_paths_mapping[category] = temp_category_paths
            self.categories_length.append(paths_length)
            self.length += paths_length

        self.shuffle_dataset()

    def update_dataset(self, image_label_pair):
        # image_label_pair --> [[path of image,name of category],[path...,category],...]
        for pair in image_label_pair:
            image_path = os.path.abspath(pair[0])
            category = pair[1]
            label = [0] * self.number_categories
            label[self.categories.index(category)] = 1

            self.images_paths.append(image_path)
            self.labels.extend(label)
            self.length += 1

    def update_categories(self, new_categories):
        pass

    def get_training_batch(self):
        start_index = self.current_count
        end_index = min(start_index + self.batch_size, self.length)
        self.current_count = end_index
        return self.read_images(self.images_paths[start_index:end_index]), np.asarray(self.labels[start_index:end_index])
