import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt


Frame_length=1024
Hop_length=512
fileName="carro-Samsung-S10(2)-Buzina"#wav file
y,sr=librosa.load('SonsMix/EngineSounds/'+fileName+'.wav')
percent=0.85#0.85
normalize_feature=True
plot_rms=True
    
import sklearn
# Normalizing for visualisation
def normalize(y, axis=0):
    if normalize_feature: 
        return sklearn.preprocessing.minmax_scale(y, axis=axis)
    return y

plt.figure(figsize=(12, 8))
if plot_rms:
    rms=librosa.feature.rms(y)[0]
    
    frames=range(len(rms))
    t=librosa.frames_to_time(frames,hop_length=Hop_length)

    plt.subplot(2,2,1)
    librosa.display.waveplot(y, alpha=0.5)
    plt.xlabel('')
    plt.title('RMS')
    
    plt.plot(t,normalize(rms),color='r')


plt.subplot(2,2,2)
librosa.display.waveplot(y, alpha=0.5)
plt.xlabel('')

odf_default  = librosa.onset.onset_strength(y=y,sr=sr,hop_length=Hop_length)
frame_time = librosa.frames_to_time(np.arange(len(odf_default)),
                                    sr=sr,
                                    hop_length=Hop_length)
onset_default = librosa.onset.onset_detect(y=y, sr=sr, hop_length=Hop_length,
                                           units='time')


plt.title('Spectral Flux')
plt.plot(frame_time, normalize(odf_default), label='Spectral flux',color="r")


spectral_centroids = librosa.feature.spectral_centroid(y, sr=sr)[0]
frames = range(len(spectral_centroids))
t = librosa.frames_to_time(frames)

if not plot_rms:
    plt.subplot(2,2,1)
    librosa.display.waveplot(y, sr=sr, alpha=0.4)
    
    
    plt.title('Spectral Centroid')
    plt.xlabel('')
    plt.plot(t, normalize(spectral_centroids), color='b')

spectral_rolloff = librosa.feature.spectral_rolloff(y, sr=sr,roll_percent=percent)[0]
plt.subplot(2,2,4)
librosa.display.waveplot(y, sr=sr, alpha=0.4)

plt.title('Spectral rolloff')
plt.plot(t, normalize(spectral_rolloff), color='b')

zcr = librosa.feature.zero_crossing_rate(y,frame_length=Frame_length)[0]
frames=range(len(zcr))
t=librosa.frames_to_time(frames,hop_length=Hop_length)

plt.subplot(2,2,3)
librosa.display.waveplot(y, sr=sr, alpha=0.4)
plt.title('Zero Crossing Rate')
plt.plot(t, normalize(zcr), color='b')

"""if normalize_feature:
    plt.savefig("SonsMix/EngineSounds/"+fileName+"_features.png")
plt.savefig("SonsMix/EngineSounds/"+fileName+"_features-non-normalized.png")"""
