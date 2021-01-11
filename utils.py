import cvlib
import cv2
import face_recognition as fr
import numpy as np
import os
import pickle
import shutil


WIDTH = 300
HEIGHT = 450


def cvlib_to_dlib_format(face_locations):
	ret = []
	for face_location in face_locations:
		x1, y1, x2, y2 = face_location
		ret.append([y1, x2, y2, x1])
	return ret

def get_face_encodings_from_image_path(
		image_path, find_faces=True, use_cvlib=False, use_large_model=False):
	image = fr.load_image_file(image_path)
	return get_face_encodings_from_image(
		image, find_faces=find_faces, use_cvlib=use_cvlib, use_large_model=use_large_model)


def get_face_encodings_from_image(
		image, find_faces=True, use_cvlib=False, use_large_model=False):
	dlib_face_locations = None
	if find_faces:
		if use_cvlib:
			faces, _ = cvlib.detect_face(image[:, :, ::-1]) # Since fr uses RGB and cvlib uses BGR format
			dlib_face_locations = cvlib_to_dlib_format(faces)
		else:
			dlib_face_locations = fr.face_locations(image)
	else:
		# Complete image is a face
		h, w = image.shape[:2]
		dlib_face_locations = [[0, w-1, h-1, 0]]
		cv2.imshow("Image", image)
		cv2.waitKey(0)
		cv2.destroyWindow("Image")
	if use_large_model:
		face_encodings = fr.face_encodings(image, dlib_face_locations, model="large")
	else:
		face_encodings = fr.face_encodings(image, dlib_face_locations)
	return face_encodings, dlib_face_locations


def load_encodings(encodings_pickle):
	with open(encodings_pickle, 'rb') as f:
		face_encodings = pickle.load(f)

	path_name_encodings = []
	for person, image_encodings in face_encodings.items():
		for image, encoding in image_encodings.items():
			path_name_encodings.append([image, person, encoding])
	
	return path_name_encodings