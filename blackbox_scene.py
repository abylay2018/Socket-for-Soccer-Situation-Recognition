import os , sys
import base64
import numpy as np
from numpy import array
import cv2
import io
from PIL import Image
from io import StringIO
import json
from socketIO_client import SocketIO
cd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cd)
from keras.models import Model
from keras.preprocessing import image as keras_image
from keras.utils import np_utils
import timeit
model_path = os.path.join('..','models','keras','models')

sys.path.append(model_path)

import resnet50

host = '10.1.198.176'
port = 5000

detection_frequency = 30

def whichScenario(i):
   return {
	5:"Outfield",
	2:"Goal Attack",
	8:"Yellow/Red Card",
	0:"LogoView",
	7:"Corner Kick",
	4:"Midfield"
   }.get(i, "Unknown scene")


class SceneRecognitionBlackbox:
			
	def __init__(self, io, detector, detection_frequency):
		self.io=io
		self.detector = detector
		self.frame_counter = 0
		self.detection_frequency = detection_frequency
		self.detect = True
		self.scene = "Unknown scene"

	def incrementFrame(self):
		self.detect = self.frame_counter % self.detection_frequency == 0
		self.frame_counter += 1
	
	def controller(self, data):
		image_jpg = base64.b64decode(data)
		image_as_np = np.frombuffer(image_jpg, dtype=np.uint8)
		image = cv2.imdecode(image_as_np, flags=1)
		image = cv2.resize(image, (224, 224))
		#image = data
		self.incrementFrame()
		if self.detect:
			x = keras_image.img_to_array(image, data_format=None)

			rescale = 1. / 255
			x = x*rescale
			x = np.expand_dims(x, axis=0)
			self.scene = self.detector.predict(x)
    		#classes = np_utils.normalize(result)
			#result = feature_model.predict(x)
			self.scene = np.argmax(self.scene)
			print(whichScenario(self.scene))
			self.io.send(whichScenario(self.scene))	
		self.io.send(whichScenario(self.scene))

	def run(self):
		self.io.connect()
		self.io.listen(self.controller)
		self.io.disconnect()


class SocketInputOutput:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socketio = SocketIO(host, port)
		print("top line is not working")

	def connect(self):
		self.socketio.on('connect', self.connected_callback)
		self.socketio.on('reconnect', self.reconnected_callback)
		self.socketio.on('disconnect', self.disconnected_callback)
		self.socketio.emit('join', 'SR')

	def disconnect(self):
		self.socketio.emit('leave', 'SR')

	def listen(self, x):
		self.socketio.on('video_stream', x)
		self.socketio.wait()

	def send(self, data):
		self.socketio.emit('SR', data)

	def connected_callback(self):
		print("Connected to server: " + self.host + ":" + self.port + "!")

	def reconnected_callback(self):
		print("Reconnected to server: " + self.host + ":" + self.port + "!")

	def disconnected_callback(self):
		print("Disconnected from server: " + self.host + ":" + self.port + "!")
   
	def objectupdate(self, data):
		return scenes
	def listener(self, data):
		print('received => ', len(data))
		scenes=self.objectupdate(data)
		self.socketio.emit('SR', scenes)
		print('sent => ', scenes)


scenes = ['offside', 'penalty', 'corner', 'outside', 'freekick', 'game']

if __name__ == '__main__':
	weights_path = '/home/papa/Desktop/hub/yeldar/sp/resnet/weights_resnet50.h5'
	weights_path = os.path.abspath(weights_path)
	model = resnet50.ResNet50(weights_path=weights_path)

	model.compile(loss='categorical_crossentropy', optimizer='sgd')
   
	io = SocketInputOutput(host, port)

	SceneRecognitionBlackbox(io, model, detection_frequency).run()






























