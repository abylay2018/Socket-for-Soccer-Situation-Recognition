
# Imports
import os, sys
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

sys.path.insert(0, os.path.join(cd, 'libs'))

from darkflow.net.build import TFNet

import random

# Server parameters
host = '10.1.198.176'
port = 5000


# Detection and tracking parameters
detection_frequency = 30  # Detects every 30 frames


class ObjectRecognitionBlackbox:
    def __init__(self, io, detector, tracker, detection_frequency):
        self.io = io
        self.detector = detector
        self.tracker = tracker
        self.frame_counter = 0
        self.detection_frequency = detection_frequency
        self.detect = True
        self.players_table = []
        self.current_players = []
        self.id_counter = 0

    def incrementFrame(self):
        self.detect = self.frame_counter % self.detection_frequency == 0
        self.frame_counter += 1

    def controller(self, data):
        image_jpg = base64.b64decode(data)
        image_as_np = np.frombuffer(image_jpg, dtype=np.uint8)
        image = cv2.imdecode(image_as_np, flags=1)

        # filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
        # with open(filename, 'wb') as f:
        #     f.write(image)
        #image = array(image)
        #image = np.frombuffer(image, dtype=np.uint8)
        #image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        self.incrementFrame()
        if self.detect:
            print ('Frame is detectable')
            boxes = self.detector.detect(image)
            playersBoxes = self.labelBoxes(boxes)
            self.tracker.initialize_track(image, playersBoxes)
        else:
            print("Tracking boxes")
            ok, screen_players = self.tracker.track(image)
            # print (ok, screen_players)
            self.updateCurrentPlayers(screen_players)

        print ('Current players', self.current_players)
        print (type(self.current_players))
        self.io.send(json.dumps(self.current_players))
        filename = 'some_image'+str(0)+'.jpg'
        img = cv2.rectangle(image_jpg,(384,0),(510,128),(0,255,0),3)
        with open(filename, 'wb') as f:
            f.write(img)
        

    def updateCurrentPlayers(self, screen_players):
        for i in range(len(screen_players)):
            # self.current_players[i]["box"] = screen_players[i]
            # below lines were added
            self.current_players[i]['lx'] = screen_players[i][0]
            self.current_players[i]['ly'] = screen_players[i][1]
            self.current_players[i]['rx'] = screen_players[i][2]
            self.current_players[i]['ry'] = screen_players[i][3]

        print ('TYPE OF UPDATED PLAYERS: ', type(self.current_players))

    def labelBoxes(self, boxes):
        res = []
        new_players = []
        for box in boxes:
            x = box["topleft"]["x"]
            y = box["topleft"]["y"]
            h = box["bottomright"]["y"] - y
            w = box["bottomright"]["x"] - x
            # below code was commented out
            # id = self.identifyPlayer({x, y, h, w})
            new_players.append({
               "name": 'all',
               "lx": x,
               "ly": y,
               "rx": h,
               "ry": w
            })
            res.append((x, y, h, w))
        self.current_players = new_players
        return res

    def identifyPlayer(self, box):
        (x, y, h, w) = box
        areas = []
        for pl in self.current_players:
            # b = pl["box"]
            # x1 = b[0]
            # y1 = b[1]
            # h1 = b[2]
            # w1 = b[3]
            x1 = pl['lx']
            y1 = pl['ly']
            h1 = pl['rx']
            w1 = pl['ry']
            left = max(x1, x)
            right = min(x1 + w1, x + w)
            top = max(y1, y)
            bottom = max(y1 + h1, y + h)
            area = ((right - left) *
                    (bottom - top)) if right > left and bottom > top else 0
            areas.append(area / (h * w))
        if len(areas) > 0:
            maxind = np.argmax(areas)
        if len(areas) <= 0 or areas[maxind] < 0.7:
            id = self.id_counter
            self.id_counter += 1
        else:
            # id = self.current_players[maxind]['id']

            del self.current_players[maxind]
        return id

    def run(self):
        self.io.connect()
        print("dddddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
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
        self.socketio.emit('join', 'OR')

    def disconnect(self):
        self.socketio.emit('leave', 'OR')

    def listen(self, x):
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.socketio.on('video_stream', x)
        print("wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww")
        self.socketio.wait()

    def send(self, data):
        self.socketio.emit('OR', data)

    def connected_callback(self):
        print("Connected to server: " + self.host + ":" + self.port + "!")

    def reconnected_callback(self):
        print("Reconnected to server: " + self.host + ":" + self.port + "!")

    def disconnected_callback(self):
        print("Disconnected from server: " + self.host + ":" + self.port + "!")
   
    def objectupdate(self, data):
        return objects

    def listener(self, data):
        print('received => ', len(data))
        objects=self.objectupdate(data)
        self.socketio.emit('OR', objects)
        print('sent => ', objects)




class FileInputOutput:
    def __init__(self, filename):
        self.filename = filename

    def connect(self):
        self.video = cv2.VideoCapture(self.filename)
        if not self.video.isOpened():
            print("Could not open video")
            sys.exit()

    def disconnect(self):
        self.video.release()

    def listen(self, listener):
        while True:
            # Read a new frame
            ok, frame = self.video.read()
            if not ok:
                break
            listener(frame)

    def send(self, data):
        print(data)


class YoloDetector:
    def __init__(self):
        self.options = {
            "model": "yolov2.cfg",
            "load": "yolov2.weights",
            "threshold": 0.35
        }
        self.tfnet = TFNet(self.options)

    def detect(self, imgcv):
        return self.tfnet.return_predict(imgcv)


class OpenCVTracker:
    def __init__(self):
        pass

    def initialize_track(self, image, boxes):
        # return boxes
        self.tracker = cv2.MultiTracker_create()
        for box in boxes:
            self.tracker.add(cv2.TrackerMedianFlow_create(), image, box)

    def track(self, image):
        return self.tracker.update(image)


names = ['Ronaldo', 'Messi', 'ball', 'referee']
width, height = 1000, 1000
objects = []
for name in names:
  lx = random.randint(0, width - 100)
  ly = random.randint(0, height - 100)
  rx = random.randint(lx + 100, width)
  ry = random.randint(ly + 100, height)
  objects.append({
      'name': name,
      'lx': lx,
      'ly': ly,
      'rx': rx,
      'ry': ry
  })


print(__name__)
if __name__ == '__main__':
    print('sdgdsgdsg')
    print(__name__)
    io = SocketInputOutput(host, port)
    #io = FileInputOutput('test1.mp4')
    #io.connect()
    #io.listen(io.listener)
    print("here")
    detector = YoloDetector()
    tracker = OpenCVTracker()
    ObjectRecognitionBlackbox(io, detector, tracker, detection_frequency).run()

