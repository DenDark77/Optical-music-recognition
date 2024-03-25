import cv2
import numpy as np
from box import Box
from train import *
import os
import pickle


def predict(img):
    if not os.path.exists('trained_models/nn_trained_model_hog.sav'):
        print('Please wait while training the NN-HOG model....')

    model = pickle.load(open('trained_models/nn_trained_model_hog.sav', 'rb'))
    features = extract_features(img, 'hog')
    labels = model.predict([features])

    return labels