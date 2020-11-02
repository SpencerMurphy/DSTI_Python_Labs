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
	def __init__(self,socketio, video_source=0,nb_predicted_images = 60):
		"""
		This function initialize the class Camera
		Args:
		-----
		- socketio : the socket object to communicate with the front end
		- video_source : the id of the camera. This should enable to connect several cameras at the same time to the server
		- nb_predicted_images : the number of prediction done before sending the result of the prediction 
		Returns:
		--------
		-  None
		"""
		self.video_source = video_source
		self.socketio = socketio
		self.nb_predicted_images = nb_predicted_images
		# get the videoCapture instance from the cv2 library
		self.camera = cv2.VideoCapture(self.video_source)
		self.frames = []
		self._predictions = []
		# flag to know if the thread responsible for getting the frames is running
		self.isrunning = False

	def reset(self):
		"""
		This function reset the properites of an Camera instance
		Args:
		-----
		- None
		Returns:
		--------
		-  None
		"""

		self.frames = []
		self._predictions = []
		self.camera.open(self.video_source)


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
			print("starting thread")
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


	def get_frame_thumb(self):
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
		global thread

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

			classes = ['UP','DOWN','UNKNOWN']
			# look at the higher probability among up/down/unknown
			# if prediction under 50% probability, return -1/No Prediction
			pred_class_idx = np.zeros(1)
			if np.max(pred,axis=1)[0] > 0.5:
				pred_class_idx = np.argmax(pred, axis=1)
				text = "{}".format(classes[pred_class_idx[0]])

			else:
				pred_class_idx[0] = -1
				text = "No Prediction"
			# store the prediction
			self._predictions.append(pred_class_idx[0])
			# add the prediction using a text, on the image
			cv2.putText(img2, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 0, 255), 5)
			#encode the image in a .png file
			img = cv2.imencode('.png', img2)[1].tobytes()

			# if the number of images to analyse is reached the answer is send to the front end
			if len(self._predictions) > self.nb_predicted_images:
				# stop camera
				self.stop()
				thread = None
				self.frames = []
				# count the number of up and the number of down among all the predictions
				# if more then 10% of the images are predicted as up or as down then takes the most predicted one
				# if not return unknown
				up = np.sum(np.array(self._predictions) == 0)
				down = np.sum(np.array(self._predictions) == 1)
				if up >= down and up > (self.nb_predicted_images / 10):
					print("up")
					# 0 for UP
					self.socketio.emit('newnumber', {'number': 0}, namespace='/start')
				elif up < down and down > self.nb_predicted_images / 10:
					print("down")
					# 1 for DOWN
					self.socketio.emit('newnumber', {'number': 1}, namespace='/start')
				else:
					print("unknown")
					# 2 for UNKNOWN
					self.socketio.emit('newnumber', {'number': 2}, namespace='/start')
		# if not image yet from the camera then just send a default image
		else:
			with open("images/0.jpg","rb") as f:
				img = f.read()			
		return img

	def get_frame_fruit(self):
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
		global thread

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
			# if prediction under 50% probability, return -1/No Prediction
			pred_class_idx = np.zeros(1)
			if np.max(pred,axis=1)[0] > 0.5:
				pred_class_idx = np.argmax(pred, axis=1)
				text = "{}".format(classes[pred_class_idx[0]])

			else:
				pred_class_idx[0] = -1
				text = "No Prediction"
			# store the prediction
			self._predictions.append(pred_class_idx[0])
			# add the prediction using a text, on the image
			cv2.putText(img2, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 0, 255), 5)
			#encode the image in a .png file
			img = cv2.imencode('.png', img2)[1].tobytes()

			# if the number of images to analyse is reached the answer is send to the front end
			if len(self._predictions) > self.nb_predicted_images:
				# stop camera
				self.stop()
				thread = None
				self.frames = []
				up = np.sum(np.array(self._predictions) == 0)
				down = np.sum(np.array(self._predictions) == 1)
				if up >= down and up > (self.nb_predicted_images / 10):
					print("up")
					self.socketio.emit('newnumber', {'number': 10}, namespace='/start')
				elif up < down and down > self.nb_predicted_images / 10:
					print("down")
					self.socketio.emit('newnumber', {'number': 11}, namespace='/start')
				else:
					print("unknown")
					self.socketio.emit('newnumber', {'number': 12}, namespace='/start')
		# if not image yet from the camera then just send a default image
		else:
			with open("images/0.jpg","rb") as f:
				img = f.read()			
		return img
