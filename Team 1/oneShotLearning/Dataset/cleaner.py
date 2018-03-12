import os
from scipy import misc
def main():
    rootdir = '/home/unagi/IndianFoodRecognition/oneShotLearning/Dataset/Train'
    for subdir, dir, files in os.walk(rootdir):
        if len(files) > 0:
            for file in files:
                path = os.path.join(subdir,file)
                try:
                    print(path)
                    img = misc.imread(path,'L')
                except:
                    print('Bad file: ',path)

if __name__ == '__main__':
    main()
