import cv2
import threading
import time
import numpy as np
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input as preprocess_input_vgg
from keras.models import load_model

# load the weights of the thumb detection model
model_thumb = load_model("model/weights_thumb_v1.h5")
model_thumb.optimizer.lr

# initialiaze a global variable for thread
thread = None


class Camera:
	"""
    This Class define the bahavior of a camera connected to the server
	"""
	def __init__(self,video_source=0):
		"""
		This function initialize the class Camera
		Args:
		-----
		- video_source : the id of the camera. This should enable to connect several cameras at the same time to the server
		Returns:
		--------
		-  None
		"""
		self.video_source = video_source
		# get the videoCapture instance from the cv2 library
		self.camera = cv2.VideoCapture(self.video_source)
		self.frames = []
		# flag to know if the thread responsible for getting the frames is running
		self.isrunning = False
	def __del__(self):
		"""
		This function delete the class Camera
		Args:
		-----
		- None
		Returns:
		--------
		- None
		"""		
		self.camera.release(self.camera.video_source)
	def run(self):
		"""
		This function start a thread in which the frame acquisition will be done
		Args:
		-----
		- None
		Returns:
		--------
		- None
		"""
		global thread
		# only create a thread the first time this function is called
		if thread is None:
			# build and start a thread running _capture_loop
			thread = threading.Thread(target=self._capture_loop,daemon=True)
			self.isrunning = True
			thread.start()

	def _capture_loop(self):
		"""
		This function update the property frames with the image read from the camera flow
		Args:
		-----
		- None
		Returns:
		--------
		- None
		"""
		# as long as the thread is running, we get images from the camera
		while self.isrunning:
			v,im = self.camera.read()
			# if the read works well then we store the image in the frames property
			if v:
				self.frames = im
		# when stopping the thread, we stop the camera
		self.camera.release()
		

	def stop(self):
		"""
		This function stop the thread
		Args:
		-----
		- None
		Returns:
		--------
		- None
		"""
		self.isrunning = False


	def get_frame(self):
		"""
		This function realize the prediction and show the result of this prediction on the frame
		Args:
		-----
		- None
		Returns:
		--------
		- None
		"""
		# use the model_variable as global
		global model_thumb
		# if an image has already been set into frames variable
		if len(self.frames)>0:
			img2 = self.frames
			# flip the image to better feeling on the screen
			img2 = cv2.flip(img2, 1)
			# add a red rectangle on the image (where the thumb will be detected)
			cv2.rectangle(img2, (300, 50), (550, 300), (0, 0, 255), 0)
			# for the prediction we just keep this rectangle
			img_array = cv2.resize(img2[50:300,300:550], (224, 224))
			# pre traitment of the image before prediction
			img_expanded = np.expand_dims(img_array, axis=0)
			preprocessed_image = preprocess_input_vgg(img_expanded)
			# the prediction is done here and put into pred variable
			pred = model_thumb.predict(preprocessed_image)
			#print(round(pred[0][0],2),round(pred[0][1],2),round(pred[0][2],2))

			classes = ['UP','DOWN','UNKNOWN']
			# look at the higher probability among up/down/unknown
			pred_class_idx = np.argmax(pred, axis=1)
			text = "{}".format(classes[pred_class_idx[0]])
			# add the prediction using a text, on the image
			cv2.putText(img2, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 0, 255), 5)
			#encode the image in a .png file
			img = cv2.imencode('.png', img2)[1].tobytes()
		# if not image yet from the camera then just send a default image
		else:
			with open("images/0.jpg","rb") as f:
				img = f.read()			
		return img

