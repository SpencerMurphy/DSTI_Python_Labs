from flask import Flask, redirect, url_for, render_template, request, Response
from camera import Camera


# get an instance of the Camera Class
# use by default the videosource = 0 
camera = Camera()

# get an instance of the Flask application
app = Flask(__name__)

def gen(camera):
    """
    Function defined to create a generator : this generator get a frame( image) 
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
        frame = camera.get_frame()
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
    -  POST : redicrect to the route /fruit_result (temporary code)specific structure return by the yield function including the frame
    """
    if request.method == "POST":
        return redirect(url_for("fruit_result"))
    else:
        return render_template("index.html")

@app.route('/fruit_result')
def fruit_result():
    """
    This function treat the behavior of the fruit_result page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template fruit_result.html when the client connect to it. Simulate the fact that a banana has benn predicted
             and send the text "banana" to be displayed on the web page
    -  		 After a timer time redirect to the route /thumb_video
    """
    # use a global Timer_wait variable. Since a refresh of the web page has been set 
    # this function is called every 5 seconds. So after 5 seconds the function redirect to
    # the route /fruit_result.html
    # THIS IS A TEMPORARY SOLUTION TO GO TO NEXT PAGE WITHOUT INTERACTION OF THE USER
    global Timer_wait
    Timer_wait += 1
    # 
    if Timer_wait < 2:
        # here the fixe value of fruit is TEMPORARY : should be the result of a prediction
        # the "fruit" value is dynamically rendered in the fruit_result.html page
        return render_template('fruit_result.html',fruit = "banana")
    else:
        return redirect(url_for("thumb_video"))

@app.route('/thumb_video', methods=["POST", "GET"])
def thumb_video():
    """
    This function treat the behavior of the thumb_video page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template thumb_video.html . Simulate the fact that a banana has benn predicted
             and send the text "banana" to be displayed on the web page
    -  POST : redicrect to the route /thumb_result : TEMPORARY CODE this POST methods is activated by a button pressed
              on the page : the target page should be defined depending on the result of the thumb prediction
    """
    if request.method == "POST":
        # the camera is stopped because the prediction is finished
        camera.stop()
        return redirect(url_for("thumb_result"))
    else :
        # when the page is rendered, the camera is started to realize the prediction
        # the code <img src="{{ url_for('thumb_video_feed') }}"> in the thumb_video.html file
        # "call" the route /thumb_video_feed in order to get an image
        camera.run()
        return render_template('thumb_video.html')

@app.route("/thumb_video_feed")
def thumb_video_feed():
    """
    This function is "called" by the webpage "thumb_video_feed". and it deliver images to this web page using an understandable
    structure
    Args:
    -----
    - None
    Returns:
    --------
    -  a "Response" that can be displayed as an image by the web page. Using the generator to get images from the camera
    """
    return Response(gen(camera), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/thumb_result/')
def thumb_result():
    """
    This function treat the behavior of the thumb_result page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template thumb_result.html .
    """
    return render_template('thumb_result.html')

# Fruit_video not yet coded
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
    return render_template('fruit_video.html')

# fruit_manual_choice not yet coded
@app.route('/fruit_manual_choice/')
def fruit_manual_choice():
    """
    This function treat the behavior of the fruit_manual_choice page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template fruit_manual_choice.html .
    """
    return render_template('fruit_manual_choice.html')

# ticket_print not yet coded
@app.route('/ticket_print/')
def ticket_print():
    """
    This function treat the behavior of the ticket_print page
    Args:
    -----
    - None
    Returns:
    --------
    -  GET : return the template ticket_print.html .
    """
    return render_template('ticket_print.html')
   
if __name__ == "__main__":
    Timer_wait = 0
    app.run(debug=True)