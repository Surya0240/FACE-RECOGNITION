
import cv2
import os
import pickle
import shutil

from argparse import ArgumentParser
from utils import get_face_encodings_from_image_path

ENCODINGS_PICKLE_FILE = 'encodings.pkl'


def prepare_known_encodings_from_images(
		input_folder, output_path, use_cvlib=False, use_large_model=False,
		find_faces=True):
	if os.path.exists(output_path):
		with open(output_path, 'rb') as f:
			face_encodings = pickle.load(f)
	else:
		face_encodings = {}
	for person in os.listdir(input_folder):
		print(" === Preparing face encodings for {} ===".format(person))
		if person not in face_encodings:
			face_encodings[person] = {}
		encodings_dir = os.path.dirname(output_path)
		path_to_faces = os.path.join(encodings_dir, person)
		try:
			shutil.rmtree(path_to_faces)
		except Exception as e:
			pass
		os.makedirs(path_to_faces)
		path_to_person_images = os.path.join(input_folder, person)
		for image in os.listdir(path_to_person_images):
			image_path = os.path.join(path_to_person_images, image)
			if not os.path.isfile(image_path):
				continue
			encodings, face_locations = \
				get_face_encodings_from_image_path(
					image_path, find_faces=find_faces, use_cvlib=use_cvlib,
					use_large_model=use_large_model)
			try:
				face_encodings[person][image] = encodings[0]
			except:
				print("Unable to find face encodings for {}".format(image_path))
			else:
				# saving face to encodings/<person>
				img = cv2.imread(image_path)
				y1, x2, y2, x1 = face_locations[0]
				face = img[y1:y2, x1:x2]
				resized = cv2.resize(face, (100, 150),
									 interpolation=cv2.INTER_AREA)
				try:
					img_path = os.path.join(path_to_faces, image)
					cv2.imwrite(img_path, resized)
				except:
					print(image_path, "Failed")
	with open(output_path, 'wb') as f:
		pickle.dump(face_encodings, f)

	return face_encodings


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('-i', "--input-folder", required=True)
	parser.add_argument('-c', "--use-cvlib", action='store_true')
	parser.add_argument('-l', "--use-large-model", action='store_true')
	parser.add_argument('-f', "--find-faces", action='store_true')
	parser.add_argument("-o", "--output",
						help='Where to store the encodings?')
	args = parser.parse_args()
	output = args.output

	if not output:
		output = ENCODINGS_PICKLE_FILE
		if args.use_large_model:
			output = os.path.join("large", output)
		else:
			output = os.path.join("small", output)
		if args.use_cvlib:
			output = os.path.join("cvlib", output)
		else:
			output = os.path.join("default", output)
		output = os.path.join("encodings", output)

	prepare_known_encodings_from_images(
			args.input_folder, output, use_cvlib=args.use_cvlib,
			use_large_model=args.use_large_model, find_faces=args.find_faces)

'''
python prepare_reference_encodings.py \
	-i "known_images" \
	-f -c

python prepare_reference_encodings.py \
	-i "known_images_with_only_face" \
	-c

'''