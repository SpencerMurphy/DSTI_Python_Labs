import cv2
import threading
import time
import numpy as np
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input as preprocess_input_vgg
from keras.models import load_model

model_front = load_model("model/weights_thumb_v1.h5")
model_front.optimizer.lr

thread = None


class Camera:
	def __init__(self,video_source=0):
		self.video_source = video_source
		self.camera = cv2.VideoCapture(self.video_source)
		self.frames = []
		self.isrunning = False
	def __del__(self):
		self.camera.release(self.camera.video_source)
	def run(self):
		global thread
		if thread is None:
			thread = threading.Thread(target=self._capture_loop,daemon=True)
			self.isrunning = True
			thread.start()

	def _capture_loop(self):
		while self.isrunning:
			v,im = self.camera.read()
			if v:
				self.frames = im
		self.camera.release()
		

	def stop(self):
		self.isrunning = False


	def get_frame(self):
		global model_front
		if len(self.frames)>0:
			img2 = self.frames
			img2 = cv2.flip(img2, 1)
			cv2.rectangle(img2, (300, 50), (550, 300), (0, 0, 255), 0)
			img_array = cv2.resize(img2[50:300,300:550], (224, 224))
			img_expanded = np.expand_dims(img_array, axis=0)
			preprocessed_image = preprocess_input_vgg(img_expanded)
			pred = model_front.predict(preprocessed_image)
			#print(round(pred[0][0],2),round(pred[0][1],2),round(pred[0][2],2))

			classes = ['UP','DOWN','UNKNOWN']
			pred_class_idx = np.argmax(pred, axis=1)
			text = "{}".format(classes[pred_class_idx[0]])

			cv2.putText(img2, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 0, 255), 5)
			img = cv2.imencode('.png', img2)[1].tobytes()
		else:
			with open("images/0.jpg","rb") as f:
				img = f.read()			
		return img

