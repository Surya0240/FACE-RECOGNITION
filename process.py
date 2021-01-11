from datetime import datetime
import numpy as np
import imagezmq
import pymongo 
import argparse
import cv2
import os
from random import randint

from recognize_face import recoginize_face_in_image

from argparse import ArgumentParser
from config import CONFIG
from utils import load_encodings
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["Log"]
mycol = mydb["Employees"]

UNKNOWN_IMAGES_DIR = "unknown_images"

def get_frames_and_process(
		path_name_encodings, threshold, use_cvlib, use_large_model, cam_num):
	imageHub = imagezmq.ImageHub()
	print("Waiting for the camera feed..")
	while True:
		(rpiName, frame) = imageHub.recv_image()
		imageHub.send_reply(b'OK')
		processed_image, names, unknown_images = \
			recoginize_face_in_image(
				frame, path_name_encodings, threshold=threshold,
				use_cvlib=use_cvlib, use_large_model=use_large_model)
		for name in names:
			mycol.insert_one({'name': name, 'datetime': datetime.now(),
							  'status': cam_num})
		now = datetime.now()
		todays_unknown = \
			os.path.join(UNKNOWN_IMAGES_DIR, now.strftime("%Y-%m-%d"))
		time = now.strftime("%H_%M_%S")
		os.makedirs(todays_unknown, exist_ok=True)
		for image in unknown_images:
			random_int = randint(1, 10)
			path = os.path.join(todays_unknown, time)
			filename = "{}-{}.jpg".format(path, random_int)
			cv2.imwrite(filename, image)
		cv2.imshow("Recognition", processed_image)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
	cv2.destroyAllWindows()	


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('-c', "--use-cvlib", action='store_true')
	parser.add_argument('-l', "--use-large-model", action='store_true')
	parser.add_argument('-t', "--threshold", default=0.5, type=float)
	parser.add_argument("-n", '--number', default=0)
	args = parser.parse_args()
	
	detect_model = ('use_cvlib' if args.use_cvlib else 'default')
	model_type = ('large' if args.use_large_model else 'small')

	encodings_pickle = CONFIG[detect_model][model_type]

	path_name_encodings = load_encodings(encodings_pickle)

	get_frames_and_process(
		path_name_encodings, args.threshold, args.use_cvlib,
		args.use_large_model, args.number)
