import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
Frame_length=1024
Hop_length=512
fileName="carro-Samsung-S10(2)-Buzina"#wav file
y,sr=librosa.load('SonsMix/EngineSounds/'+fileName+'.wav')
percent=0.85
normalize_feature=True

import sklearn
# Normalizing for visualisation
def normalize(y, axis=0):
    if normalize_feature: 
        return sklearn.preprocessing.minmax_scale(y, axis=axis)
    return y
seg_size=Frame_length*12
rms=[]
odf_default=[]
spectral_rolloff=[]
spectral_centroids=[]
i=0
while len(y)>=i:
        data=y[i:seg_size+i]
        rms=np.concatenate([rms,normalize(librosa.feature.rms(data,frame_length=Frame_length,hop_length=Hop_length)[0])])
        odf_default=np.concatenate([odf_default,normalize(librosa.onset.onset_strength(data, sr=sr,hop_length=Hop_length))])
        spectral_rolloff=np.concatenate([spectral_rolloff,normalize(librosa.feature.spectral_rolloff(data, sr=sr,roll_percent=percent)[0])])
        spectral_centroids=np.concatenate([spectral_centroids,normalize(librosa.feature.spectral_centroid(data, sr=sr)[0])])
        i+=seg_size
        
plt.figure(figsize=(12,4))
frames=range(len(rms))
t=librosa.frames_to_time(frames,hop_length=Hop_length)
plt.figure(figsize=(12, 8))
plt.subplot(2,2,1)
librosa.display.waveplot(y, alpha=0.5)
plt.xlabel('')
plt.title('RMS')

plt.plot(t,rms,color='r')
plt.subplot(2,2,2)
librosa.display.waveplot(y, alpha=0.5)
plt.xlabel('')

frame_time = librosa.frames_to_time(np.arange(len(odf_default)),
                                    sr=sr,
                                    hop_length=Hop_length)
onset_default = librosa.onset.onset_detect(y=y, sr=sr, hop_length=Hop_length,
                                           units='time')

plt.title('Spectral Flux')
plt.plot(frame_time, odf_default, label='Spectral flux',color="r")

frames = range(len(spectral_centroids))
t = librosa.frames_to_time(frames)

plt.subplot(2,2,3)
librosa.display.waveplot(y, sr=sr, alpha=0.4)

plt.title('Spectral Centroid')
plt.plot(t, spectral_centroids, color='b')

plt.subplot(2,2,4)
librosa.display.waveplot(y, sr=sr, alpha=0.4)

plt.title('Spectral rolloff')
plt.plot(t, spectral_rolloff, color='b')
"""if normalize_feature:
    plt.savefig("SonsMix/EngineSounds/"+fileName+"_features.png")
plt.savefig("SonsMix/EngineSounds/"+fileName+"_features-non-normalized.png")"""

