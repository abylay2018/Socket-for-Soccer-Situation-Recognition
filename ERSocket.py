import os, sys
import base64
import numpy as np
import cv2
from socketIO_client import SocketIO
from sklearn.externals import joblib
from matplotlib import pyplot as plt
import glob
import warnings
import dlib
import math
import my_model as md

warnings.filterwarnings("ignore", category=DeprecationWarning)
cd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cd)

sys.path.insert(0, os.path.join(cd, 'libs'))

# Server parameters
host = '10.1.198.176'
port = 5000

faceDet = cv2.CascadeClassifier("/home/meruyert/emotion_recognition_test/models/haarcascade_frontalface_default.xml")
faceDet2 = cv2.CascadeClassifier("/home/meruyert/emotion_recognition_test/models/haarcascade_frontalface_alt2.xml")
faceDet3 = cv2.CascadeClassifier("/home/meruyert/emotion_recognition_test/models/haarcascade_frontalface_alt.xml")
faceDet4 = cv2.CascadeClassifier("/home/meruyert/emotion_recognition_test/models/haarcascade_frontalface_alt_tree.xml")


class EmotionRecognitionBlackbox:

	def __init__(self, io, classifier):
		self.io = io
		self.classifier = classifier

	def controller(self, data):
		 x_test = np.asarray(detect_frame(data))

		 try:
		    x_test = x_test.reshape(1, 128, 128, 1)
		    x_test = np.repeat(x_test, 3, axis = -1)
		    prediction = model.predict(x_test) #predict the new test set (real time)
		            
		    if prediction[0][0] < 0.5:
		        self.io.send("neutral")
		    else:
		        self.io.send("non-neutral")
		    except:
		          



	def detect_frame(self, data):
	    #pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)  
	    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	    gray = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
	    clahe_image = clahe.apply(gray)
	    cv2.equalizeHist(clahe_image, clahe_image) #should be clahe, could use cv2.equalizeHist(gray, gray)
	        
	    face = faceDet.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
	    face2 = faceDet2.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
	    face3 = faceDet3.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
	    face4 = faceDet4.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
	            
	    if len(face) == 1:
	        facefeatures = face
	    elif len(face2) == 1:
	        facefeatures = face2
	    elif len(face3) == 1:
	        facefeatures = face3
	    elif len(face4) == 1:
	        facefeatures = face4
	    else:
	        facefeatures = ""
	    filenum += 1
	    
	    if len(facefeatures) != 0:
	        for (x, y, w, h) in facefeatures:
	            cv2.rectangle(clahe_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
	            gray = gray[y:y+h, x:x+w]
	            try:
	                out = cv2.resize(gray, (128, 128))
	                out = out/256
	                return out
	            except:
	                print("not cropped")
	                pass #If error, pass the frame	


    def run(self):
        self.io.connect()
        self.io.listen(self.controller)
        self.io.disconnect()


class SocketInputOutput:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socketio = SocketIO(host, port)

    def connect(self):
        self.socketio.on('connect', self.connected_callback)
        self.socketio.on('reconnect', self.reconnected_callback)
        self.socketio.on('disconnect', self.disconnected_callback)
        self.socketio.emit('join', 'ER')

    def disconnect(self):
        self.socketio.emit('leave', 'ER')

    def listen(self, listener):
        self.socketio.on('user_input_stream', listener)
        self.socketio.wait()

    def send(self, data):
        self.socketio.emit('ER', data)

    def connected_callback(self):
        print("Connected to server: " + self.host + ":" + self.port + "!")

    def reconnected_callback(self):
        print("Reconnected to server: " + self.host + ":" + self.port + "!")

    def disconnected_callback(self):
        print("Disconnected from server: " + self.host + ":" + self.port + "!")


if __name__ == '__main__':
	io = SocketInputOutput(host, port)
	classifier = md.tl_vgg('model_weights.h5')
	ObjectRecognitionBlackbox(io, classifier).run()