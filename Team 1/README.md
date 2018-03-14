# Team 1

This part of the project deals with recognition of the food items given an image. The current implementation includes one shot learning approaches along with Faster-RCNN. We plan to tackle the dishes for the dish ids mentioned in 'dishes.tsv'. 

## dataset_loader

This module contains the dataset loaders for various types of networks. We have three types of loaders which we tackle in this module.
1. One shot loader
2. Image Classification Loader (TODO)
3. Object Detection Loader (TODO)

### One shot loader

The file `oneshot.py` defines a class to perform dataset generation for one shot learners using siamese networks. We assume the following directory structure:
```
--Team 1
    |--dataset_loader
    |--main.py
```
Inside main.py we call the loader as follows:
```
from dataset_loader import oneshot

obj = oneshot.dataset_loader(dataset_folder, working_folder, [x, y, z], batch_size)
```
Here dataset_folder is of the structure:
```
--datset
    |--Category 1
        |--1.jpg
        |--2.jpg
        ..
    |--Category 2
    ..
```
working_folder is where the save files for the loader will be written and [x, y, z] are dimensions of the image being read. Once the constructor has been called, the images can now be retrived using the get_training_batch() method. One can repeatedly call the method to get image pairs and labels in the batch_size mentioned in the constructor call. To check whether the dataset has been exhausted, the done() can be called which return True if the case if that is indeed the case and False otherwise.
```
while not obj.done():
    left_images, right_images, labels = obj.get_training_batch()
    ...
```
`left_images` and `right_images` are numpy arrays of the shape (batch_size, x, y, z) and `labels` is of size (32, ). The counter for the get_training_batch() can be reset using the reset() method. The dataset can also be updated using update_dataset() method which expects and array of arrays having two elements. The first element is the full path of the image and the second image is the category(folder name) inside the dataset where it belongs. One can save and delete the dataset using the save_to_disk() and delete_from_disk() methods. The loader is automatically called during the constructor call if the working_folder already contains a saved copy.
