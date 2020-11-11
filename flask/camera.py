import cv2
import threading
import time
import numpy as np
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input as preprocess_input_vgg
from keras.models import load_model

from predict import YoloPredictionModel, generate_blob
from predict_classif import ClassifPredictionModel


from flask_socketio import SocketIO, emit
from threading import Thread, Event


PATH_MODEL_THUMB = "model/weights_thumb_v10112020.h5"
PATH_CLASSES_THUMB = "model/thumb.classes"


classif_thumb = ClassifPredictionModel(PATH_MODEL_THUMB, PATH_CLASSES_THUMB,(190,50,440,300))


PATH_CONFIG = "yolo_config/yolov4-custom-02.cfg"
PATH_WEIGHTS = "yolo_config/weights/yolov4-custom-02_final.weights"
PATH_CLASSES = "yolo_config/obj.names"

yolo = YoloPredictionModel(PATH_CONFIG,
                               PATH_WEIGHTS,
                               PATH_CLASSES).set_backend_and_device()

# initialiaze a global variable for thread
thread = None


class Camera:
	"""
    This Class define the bahavior of a camera connected to the server
	"""
	def __init__(self,socketio = None, video_source=0,nb_predicted_images = 60):
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
		global thread

		# if an image has already been set into frames variable
		if len(self.frames)>0:
			frame = self.frames
			# get the prediction of the actual frame
			pred_class_idx, pred_proba_value, text  = classif_thumb.predict_and_identify(frame, 0.5)

			# flip the image to better feeling on the screen
			frame = cv2.flip(frame, 1)

			# store the prediction
			self._predictions.append(pred_class_idx)
			# add the prediction using a text, on the image
			cv2.putText(frame, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,1.25, (0, 0, 255), 5)
			#encode the image in a .png file
			img = cv2.imencode('.png', frame)[1].tobytes()

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
			img2 = cv2.flip(img2, 1)
			
			img_array = cv2.resize(img2, (256, 256))

			# tranform frames into blobs
			blob_input = generate_blob(img2)
			# blobs as yolo inputs
			yolo.ingest_input(blob_input)
			# Get output obects
			layers = yolo.get_output_layers_names()
			output = yolo._forward()
			# Predictions
			classe,index,proba = yolo.predict_and_identify(img2,output,0.5)

			# get the index of the detected fruit :
			# -1 : no detection
			# 0:3 : index of fruit
			# 4 : several fruits detected
			result = result_fruit(classe,index,proba)

			# store the result on a list
			self._predictions.append(result)
		
			#encode the image in a .png file
			img = cv2.imencode('.png', img2)[1].tobytes()

			# if the number of images to analyse is reached the answer is send to the front end
			#if False:
			if len(self._predictions) > self.nb_predicted_images:
				# stop camera
				self.stop()
				thread = None
				self.frames = []
				# analyse the list of detection realised on all the images and return one detection answer
				detection = detection_fruit(classe,self._predictions)

				# send the detection to the front end
				# add 10 to the detection to create an unique code that can be used by the front end
				self.socketio.emit('newnumber', {'number': 10+detection}, namespace='/start')
			
		# if not image yet from the camera then just send a default image
		else:
			with open("images/0.jpg","rb") as f:
				img = f.read()			
		return img


	
def result_fruit(classe,index,proba):
	"""
	This function analyse the prediction and return a consolidation of the predictions done
	Args:
	-----
	- classe : list of classes
	- index : list with the index of fruit detected
	- proba : probability of the detection (not used)
	Returns:
	--------
	- fruit dtected :
		-1 : no detection
		0:3 : index of the fruit
		4 : several fruits detected
	"""
	list_indexes = classe[::2]
	#print(list_indexes)
	nb_fruit = len(list_indexes)-1 # remove the blank detection
	list_nb_indexes = [index.count(x*2)+index.count(x*2+1) for x in range(nb_fruit+1)]
	#print(list_nb_indexes)
	list_nb_fruit = list_nb_indexes[0:nb_fruit]
	nb_zeros = list_nb_fruit[0:nb_fruit].count(0)
	# if only one fruit detected (n-1 zeros) then return the index of the fruit detected
	if nb_zeros == (nb_fruit-1):
		fruit = list_nb_fruit.index(max(list_nb_fruit))
	# number of  equal number of fruit => no detection
	elif nb_zeros == nb_fruit:
		fruit = -1
	# less then n-1 fruit mean several fruits detected
	else:
		fruit = nb_fruit
	
	return fruit

def detection_fruit(classe,prediction):
	"""
	This function analyse the list of prediction and return a consolidation of the predictions done
	Args:
	-----
	- classe : list of classes
	- prediction : list of predictions
	Returns:
	--------
	- fruit
	"""
	nb_predicted_images = len(prediction)
	list_indexes = classe[::2]
	nb_fruit = len(list_indexes)-1 # remove the blank detection
	# count the number of each predicted fruit, including the number of "no prediction" and "several fruits"
	list_nb_indexes = [prediction.count(x) for x in range(-1,(nb_fruit+1))]
	# remove the number of "no prediction" from the list
	list_nb_fruit = list_nb_indexes[1:nb_fruit+2]
	# find the most detected prediction
	fruit = list_nb_fruit.index(max(list_nb_fruit))

	nb_max = list_nb_fruit[fruit]
	#if the max detected has detected more then 10% of time then this is the detection, otherwise return "no predition"
	if nb_max > (nb_predicted_images / 10):
		result = fruit
	else:
		result = -1
	return result


if __name__ == "__main__":

	classe = ['Tomato', 'Tomato (group)', 'Apple', 'Apple (group)', 'Banana', 'Banana (group)', 'Mango', 'Mango (group)', 'Blank']
	index = [-1,-1,-1,-1,-1,-1,1,-1,-1,-1,4,4,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
	proba = []
	#print(result_fruit(classe,index,proba))
	#print(detection_fruit(classe,index,len(index)))

	"""
	socketio = SocketIO(None, async_mode=None, logger=True, engineio_logger=True)
	camera_thumb = Camera(socketio, video_source = 0,nb_predicted_images = 60)

	camera_thumb.run()

	while True:
		frame = camera_thumb.get_frame_thumb()
		jpg_as_np = np.frombuffer(frame, dtype=np.uint8)
		img = cv2.imdecode(jpg_as_np, flags=1)
		cv2.imshow("test", img)
		cv2.waitKey(1)
	"""