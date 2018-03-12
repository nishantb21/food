import os
import sys
from distutils.dir_util import copy_tree
import uuid
import shutil
trainFolder = '/home/unagi/phood/Team 1/ObjectDetection/Data/Train'
testFolder = '/home/unagi/phood/Team 1/ObjectDetection/Data/Test'
destination = '/home/unagi/phood/Team 1/ObjectDetection/Formated Data'
def createClasses():
    for dish in os.listdir(trainFolder):
        if not os.path.exists(os.path.join(destination,dish)):
            os.makedirs(os.path.join(destination,dish))
    return os.listdir(trainFolder)
def createPositives(dishes):
    for i in dishes:
        orgPath = os.path.join(trainFolder,i)
        path = os.path.join(destination,i)
        destPath = os.path.join(path,'positive')
        if not os.path.exists(destPath):
            os.makedirs(destPath)
            copy_tree(orgPath,destPath)
def createNegatives(dishes):
    for i in dishes:
        orgPath = os.path.join(trainFolder,i)
        path = os.path.join(destination,i)
        destPath = os.path.join(path,'negative')
        if not os.path.exists(destPath):
            os.makedirs(destPath)
            for j in dishes:
                if j not in destPath:
                    newOrgPath = os.path.join(trainFolder,j)
                    for subdir, dirs, files in os.walk(newOrgPath):
                        for f in files:
                            shutil.copy(os.path.join(newOrgPath,f),os.path.join(destPath,str(uuid.uuid4())+'.jpg'))
def createTests(dishes):
    for i in dishes:
        orgPath = os.path.join(testFolder,i)
        path = os.path.join(destination,i)
        destPath = os.path.join(path,'testImages')
        if not os.path.exists(destPath):
            os.makedirs(destPath)
            copy_tree(orgPath,destPath)
def main():
    dishes = createClasses()
    createPositives(dishes)
    createNegatives(dishes)
    createTests(dishes)

if __name__ == '__main__':
    main()
