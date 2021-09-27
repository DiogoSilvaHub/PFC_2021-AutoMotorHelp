import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
import numpy as np
import librosa
import librosa.display
import time
import np_rw_buffer
import threading, queue
import pyrebase
from datetime import datetime
import sys
import soundfile

config={
    "apiKey": "AIzaSyCaPBmolfBAriSlW8mBJG1_Qv1q2pLzwos",
    "authDomain": "test-33b33.firebaseapp.com",
    "databaseURL": "https://test-33b33-default-rtdb.europe-west1.firebasedatabase.app/",
    "projectId": "test-33b33",
    "storageBucket": "test-33b33.appspot.com",
    "messagingSenderId": "754583052587",
    "appId": "1:754583052587:web:5ab024ed1e3b8c8068656e",
    "measurementId": "G-CVP2JJ01XY"
}#firestore credentials

firebase=pyrebase.initialize_app(config)
user=firebase.auth().sign_in_with_email_and_password(sys.argv[1], sys.argv[2])#email, password
storage=firebase.storage()

model = keras.models.load_model('modelMelspectrogramBinary')# load evaluator model

signal,sr=librosa.load(sys.argv[3])#load audio file in 22050 samples per second

frame_length=1024
hop_length=frame_length//2
seg_size=frame_length*22

rmsTh=0.05
sfTh=2
srMargin=2000
startTimer=22050# 1 second
min_event_length=22050//2# 0.5 seconds
time_of_long_event=10*22050# 10 seconds

buffer = np_rw_buffer.RingBuffer(seg_size*2)#start ringbuffer

event=[]#event array


def producer(name):#thread that writes in ringbuffer
    i=0
    while len(signal)>=i:
        time.sleep(1)#1 second
        data=signal[i:seg_size+i]
        buffer.write(data)  
        if np.abs(buffer._end-buffer._start)>=seg_size:#tell other thread that buffer is half-full
            q.put("read")
        i+=seg_size
    q.put(None)#send None after reading the entire signal

def evaluate_event(margin=0):
    global event
    
    if(len(event)>min_event_length):#only check event if it is long enough
        
        feature = librosa.feature.melspectrogram(y=event, sr=sr)

        feature_processed_mean = np.mean(feature.T,axis=0)
    
        feature_processed_std = np.std(feature.T,axis=0)
    
        feature_processed = np.vstack((feature_processed_mean, feature_processed_std)).T
        
        results = model(np.array([feature_processed]))
        
        results = results.numpy()
        
        if results[0][0] > results[0][1]:#if there is a anomaly
            #save event with 22050 samples per second and 16 bits per sample  
            soundfile.write('temporaryFile.wav',np.float32(event[:len(event)-1-margin]),22050,subtype='PCM_16')
            #store event in user's folder with current time
            storage.child(user["localId"]+"/"+str(datetime.now())+".wav").put('temporaryFile.wav',user["idToken"])
            print("Anomaly")
            #remove audiofile from event
            os.remove('temporaryFile.wav')

        if margin:#if there is a margin save it for the next event
            event=event[-margin:]
        else:
            event=[]

def consumer(name):#thread that reads from ringbuffer and splits events based on sound features
    global event
    srRp=0
    timer=startTimer# 1 second
    state=0
    stateEntry=True
    while True:
        get=q.get()
        if get==None:#when get is None it means producer thread has stopped
            if len(event):#if event has size bigger than 0 evaluate the last event of the file
                evaluate_event()
            break
        
        seg=np.frombuffer(buffer.read(seg_size), dtype=np.float32)#read from ringbuffer
        rms=librosa.feature.rms(seg, frame_length=frame_length,hop_length=hop_length)[0]#array of root mean square
        sf=librosa.onset.onset_strength(seg)#array of spectral flux
        sr=librosa.feature.spectral_rolloff(seg)[0]#array of spectral rolloff
        
        for i in range(0, len(rms)):#arrays of the features have the same size
            if state==0:#Disposable sound only checks rms
                if rms[i]>=rmsTh:
                    stateEntry=True
                    state=1
                    event=[]
                    
            elif state==1:#Non-stationary sound 
                timer-=hop_length
                
                if stateEntry:#every time it enters in Non-stationary entryTimer is updated to its initial value
                    stateEntry=False
                    timer=startTimer
                    
                if sf[i]>sfTh:#if flux is over its threshold stay in this state for a bit longer
                    timer=startTimer
                
                if rms[i]<rmsTh:#return to starting state
                    evaluate_event()
                    state=0
                    
                elif timer<=0:#if flux is stable pass to state Stationary 
                    evaluate_event()
                    state=2
                
                elif sr[i]<srRp-srMargin or sr[i]>srRp+srMargin:#update rolloff reference point every time it passes its margins
                        srRp=sr[i]
                        evaluate_event()
                        
                event=np.concatenate([event,seg[i*hop_length:hop_length+i*hop_length]])
                
            else:#Stationary Sound
                if rms[i]<rmsTh:#return to starting state
                    evaluate_event()
                    state=0
                    
                elif sf[i]>sfTh:#every time flux is bigger than its threshold pass to Non-Stationary state
                    evaluate_event(frame_length+hop_length)    
                    stateEntry=True
                    state=1
                    
                elif sr[i]>srRp+srMargin or sr[i]<srRp-srMargin or len(event)>=time_of_long_event:
                    #save event every time rolloff passes its margins or when event is already too long
                    if len(event)<time_of_long_event:#update rolloff reference point 
                        srRp=sr[i]
                    evaluate_event()
                    
                event=np.concatenate([event,seg[i*hop_length:hop_length+i*hop_length]])

#main
q=queue.Queue()#allows passing values ​​between threads and blocking threads

bw=threading.Thread(target=producer,args=(q,))#bufferWriter thread
pr=threading.Thread(target=consumer,args=(q,))#processing thread

pr.start()#start of consumer thread
bw.start()#start of producer thread

bw.join()#end of producer thread
pr.join()#end of consumer thread