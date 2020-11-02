from flask import Flask, redirect, url_for, render_template, request, Response
from camera import Camera

from flask_socketio import SocketIO, emit
from flask import copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event



# get an instance of the Flask application
app = Flask(__name__)
app.config['DEBUG'] = True

# create a socket to be able to communicate between the back-end and the front-end
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

# get two instances of the Camera Class
# one for fruit detection and the other for thumb detection
# nb_predicted_images : number of images used to do the prediction
camera_thumb = Camera(socketio,video_source = 0,nb_predicted_images = 60)
camera_fruit = Camera(socketio,video_source = 0,nb_predicted_images = 60)

# initialize this global variable used to store the fruit detection to None
fruit_prediction = None

def gen_thumb(camera):
    """
    Function defined to create a generator for the thumb detection : this generator get a frame( image) 
	from the camera and provide a specific structure (in the yield command) that can be send to
	the web page 
	Args:
	-----
	- camera : instance of the class Camera
	Returns:
	--------
	- specific structure return by the yield function including the frame

    """
    while True:
        frame = camera.get_frame_thumb()
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

def gen_fruit(camera):
    """
    Function defined to create a generator for the fruit detection : this generator get a frame( image) 
	from the camera and provide a specific structure (in the yield command) that can be send to
	the web page 
	Args:
	-----
	- camera : instance of the class Camera
	Returns:
	--------
	- specific structure return by the yield function including the frame

    """
    while True:
        frame = camera.get_frame_fruit()
        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

@app.route('/' , methods=["POST", "GET"])
def index():
    """
    This function treat the behavior of the index.html page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template index.html when the web client connect to it
    -  POST : redicrect to the route /fruit_video where the detection of the fruit starts
    """
    global fruit_prediction
    if request.method == "POST":
        return redirect(url_for("fruit_video"))
    else:
        fruit_prediction = None
        return render_template("index.html")


@app.route('/thumb_video/<string:predict>')
def thumb_video(predict):
    """
    This function treat the behavior of the thumb_video page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template thumb_video.html . Display which fruit has been detected 
            and start the thumb detection
    """
    # get the fruit_detection from the global variable fruit_detection and send it to
    # the thumb_video.html page to be printed
    global fruit_prediction
    fruit_prediction = predict

    # when the page is rendered, the camera is started to realize the prediction
    # the code <img src="{{ url_for('thumb_video_feed') }}"> in the thumb_video.html file
    # "call" the route /thumb_video_feed in order to get an image
    camera_thumb.reset()
    camera_thumb.run()
    return render_template('thumb_video.html',predict=fruit_prediction)

@app.route("/thumb_video_feed")
def thumb_video_feed():
    """
    This function  delivers thumb images to the thumb_video.html web page using an understandable
    structure
    Args:
    -----
    - None
    Returns:
    --------
    -  a "Response" that can be displayed as an image by the web page. Using the generator to get images from the camera
    """
    return Response(gen_thumb(camera_thumb), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/fruit_video_feed")
def fruit_video_feed():
    """
    This function  delivers thumb images to the fruit_video.html web page using an understandable
    structure
    Args:
    -----
    - None
    Returns:
    --------
    -  a "Response" that can be displayed as an image by the web page. Using the generator to get images from the camera
    """
    return Response(gen_fruit(camera_fruit), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/fruit_video/')
def fruit_video():
    """
    This function treat the behavior of the fruit_video page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template fruit_video.html .
    """
        
    # when the page is rendered, the camera is started to realize the prediction
    # the code <img src="{{ url_for('fruit_video_feed') }}"> in the fruit_video.html file
    # "call" the route /thumb_video_feed in order to get an image
    camera_fruit.reset()
    camera_fruit.run()
    return render_template('fruit_video.html')

@app.route('/fruit_manual_choice/', methods=["POST", "GET"])
def fruit_manual_choice():
    """
    This function treat the behavior of the fruit_manual_choice page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template fruit_manual_choice.html 
    -  POST : Treat the answer to the manual validation of the fruit.
            go back to index page if the answer is no
            print the ticket if the answer is yes
    """
    global fruit_prediction
    if request.method == 'POST':
        if request.form['yesno'] == 'Yes':
            return redirect(url_for("ticket_printing"))
        elif request.form['yesno'] == 'No':
            return redirect(url_for("index"))
        else:
            pass # unknown
    else : #GET
        # get the fruit_detection from the global variable fruit_detection and send it to
        # the fruit_manual_choice.html page to be printed
        return render_template('fruit_manual_choice.html', predict = fruit_prediction)

# ticket_print not yet coded
@app.route('/ticket_printing/')
def ticket_printing():
    """
    This function treat the behavior of the ticket_print page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template ticket_printing.html .
    """
    # get the fruit_detection from the global variable fruit_detection and send it to
    # the ticket_printitng.html page to be printed
    global fruit_prediction
    return render_template('ticket_printing.html', predict = fruit_prediction)

@socketio.on('connect', namespace='/start')
def start_connect():
    """
    This function is called at initialization by the front end of the socket
    Args:
    -----
    - namespace
    Returns:
    --------
    -  None
    """
    print('Client connected')

   
if __name__ == "__main__":
    Timer_wait = 0
    socketio.run(app)