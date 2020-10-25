from flask import Flask, redirect, url_for, render_template, request, Response
#from capture import capture_and_save
from camera import Camera



camera = Camera()


app = Flask(__name__)

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
			   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')


@app.route('/' , methods=["POST", "GET"])
def index():
	if request.method == "POST":
		return redirect(url_for("fruit_result"))
	else:
		return render_template("index.html")

@app.route('/fruit_result')
def fruit_result():
	global Timer_wait
	Timer_wait += 1
	if Timer_wait < 2:
		return render_template('fruit_result.html',fruit = "banana")
	else:
		return redirect(url_for("thumb_video"))

@app.route('/thumb_video', methods=["POST", "GET"])
def thumb_video():
	if request.method == "POST":
		camera.stop()
		return redirect(url_for("thumb_result"))
	else :
		camera.run()
		return render_template('thumb_video.html')

@app.route("/thumb_video_feed")
def thumb_video_feed():
	return Response(gen(camera), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/thumb_result/')
def thumb_result():
	return render_template('thumb_result.html')

# Fruit_video not yet coded
@app.route('/fruit_video/')
def fruit_video():
	return render_template('fruit_video.html')

# fruit_manual_choice not yet coded
@app.route('/fruit_manual_choice/')
def fruit_manual_choice():
	return render_template('fruit_manual_choice.html')

# ticket_print not yet coded
@app.route('/ticket_print/')
def ticket_print():
	return render_template('ticket_print.html')
   
if __name__ == "__main__":
	Timer_wait = 0
	app.run(debug=True)