#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 08:04:23 2021

@author: diogo_silva
"""

#### Dependencies ####
import numpy as np
import librosa
import librosa.display
import os
import time

#   This code needs a dataset of sounds saved in a file called EngineSounds with two inner files
# called anomaly and engine 

startTime = time.time()

# Create a list of the categories
categories = 'anomaly engine'.split()

def extract_features(file_name):
    audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast') 
    melspectrogram = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
    melspectrogram_mean = np.mean(melspectrogram.T,axis=0)
    
    melspectrogram_std = np.std(melspectrogram.T,axis=0)

    melspectrogram_processed = np.vstack((melspectrogram_mean, melspectrogram_std)).T
     
    return melspectrogram_processed

# Iterate through each sound file and extract the features
for category in categories:
    for filename in os.listdir(f'./EngineSounds/{category}'):
        
        melspectrogram = extract_features(f'./EngineSounds/{category}/{filename}')
        
        np.savetxt(f'./MelspectrogramBinary/{category}/{filename.split(".")[0]}-melspectrogram.csv', melspectrogram, delimiter=",")

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))

