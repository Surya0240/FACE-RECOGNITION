import cv2
import imagezmq
import os
import pymongo
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from argparse import ArgumentParser
from datetime import datetime, timedelta
from random import randint
from utils import load_encodings

from config import CONFIG
from recognize_face import recoginize_face_in_image

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["Log"]
mycol = mydb["Employees"]

UNKNOWN_IMAGES_DIR = "unknown_images"

def process_frame(frame, path_name_encodings, last_datetime_by_name,
				  threshold=0.5, use_cvlib=False, use_large_model=False,
				  cam_num=0):
	processed_image, names, unknown_images = \
		recoginize_face_in_image(
			frame, path_name_encodings, threshold=threshold,
			use_cvlib=use_cvlib, use_large_model=use_large_model)
	now = datetime.now()
	for name in names:
		todays_unknown = \
			os.path.join(UNKNOWN_IMAGES_DIR, now.strftime("%Y-%m-%d"))
		time = now.strftime("%H_%M_%S")
		os.makedirs(todays_unknown, exist_ok=True)
		for image in unknown_images:
			random_int = randint(1, 10)
			path = os.path.join(todays_unknown, time)
			filename = "{}-{}.jpg".format(path, random_int)
			try:
				cv2.imwrite(filename, image)
			except:
				pass
		try:
			dd = now - last_datetime_by_name[name]
		except:
			pass
		else:
			if (dd / timedelta(minutes=1)) < 5:
				continue
		last_datetime_by_name[name] = now
		mycol.insert_one({'name': name, 'datetime': now,
						  'status': cam_num})
	processed_image = cv2.resize(processed_image, (1000, 600))
	return processed_image

	 
def sendImagesToWeb(path_name_encodings, last_datetime_by_name,
					threshold=0.4, use_cvlib=False,
					use_large_model=False, cam_num=0):
	# When we have incoming request, create a receiver and subscribe to a publisher
	imageHub = imagezmq.ImageHub()
	print("Waiting for the video stream..")
	while True:
		# Pull an image from the queue
		(rpiName, frame) = imageHub.recv_image()
		imageHub.send_reply(b'OK')
		processed_frame = \
			process_frame(frame, path_name_encodings, last_datetime_by_name,
						  threshold, use_cvlib, use_large_model, cam_num)
		# Using OpenCV library create a JPEG image from the frame we have received
		jpg = cv2.imencode('.jpg', processed_frame)[1]
		# Convert this JPEG image into a binary string that we can send to the browser via HTTP
		yield b'--frame\r\nContent-Type:image/jpeg\r\n\r\n'+jpg.tostring()+b'\r\n'

# Add `application` method to Request class and define this method here

#@app.route('/', methods=['GET','POST','OPTIONS'])
@Request.application
def application(request):
	# What we do is we `sendImagesToWeb` as Iterator (generator) and create a Response object
	# based on its output.

	encodings_pickle = CONFIG["use_cvlib"]["small"]

	path_name_encodings = load_encodings(encodings_pickle)
	current = datetime.now()
	current_minus_6mins = current - timedelta(hours=6)
	results = mycol.find({'datetime': {'$gte': current_minus_6mins}})

	last_datetime_by_name = {}
	for result in results:
		# print(result)
		name = result['name']
		if name not in last_datetime_by_name:
			last_datetime_by_name[name] = result['datetime']
		else:
			# print(last_datetime_by_name[name], result['datetime'], max(last_datetime_by_name[name], result['datetime']))
			last_datetime_by_name[name] = max(last_datetime_by_name[name], result['datetime'])

	print(f" === last_datetime_by_name: {last_datetime_by_name}")
	return Response(
		sendImagesToWeb(path_name_encodings, last_datetime_by_name,
						0.4, use_cvlib=True, use_large_model=False,
						cam_num=0),
		mimetype='multipart/x-mixed-replace; boundary=frame')
	#return make_response(sendImagesToWeb())

if __name__ == '__main__':
	# This code starts simple HTTP server that listens on interface with IP 192.168.8.72, port 4000
	run_simple('192.168.8.72', 4000, application)
	#app.run(host='localhost',port='5003', debug=True)