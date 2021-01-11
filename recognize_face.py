import cv2
import face_recognition as fr
import numpy as np
import os
import pickle

from argparse import ArgumentParser
from config import CONFIG
from utils import WIDTH, HEIGHT, get_face_encodings_from_image, load_encodings

def recoginize_face_in_image(
        image, path_name_encodings, encodings=None, threshold=0.5,
        use_cvlib=False, use_large_model=False):
    
    to_find_face_encodings, to_find_face_locations = \
        get_face_encodings_from_image(
            image, find_faces=True, use_cvlib=use_cvlib,
            use_large_model=use_large_model)

    height, width = image.shape[:2]

    names_with_locations = []

    if not encodings:
        encodings = [x[-1] for x in path_name_encodings]
    
    names = set()
    unknown_faces = []
    for to_find_face_encoding, to_find_face_location in \
            zip(to_find_face_encodings, to_find_face_locations):
        differences = fr.face_distance(encodings, to_find_face_encoding)
        differences = np.array(differences)
        
        closest_index = np.argmin(differences)

        y1, x2, y2, x1 = to_find_face_location
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.rectangle(image, (x1, y2), (x2, y2+35), (255, 0, 0), -1)
        text_y = min(y2, height)
        text_x = x1
        
        if differences[closest_index] < threshold:
            name = path_name_encodings[closest_index][1]
        else:
            name = "Unknown"
            unknown_faces.append(image[y1:y2, x1:x2])
        names.add(name)
        cv2.putText(image, name, (x1+2, y2+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
#         print(name)
    return image[:, :, ::-1], names, unknown_faces


if __name__ == "__main__":  
    parser = ArgumentParser()
    parser.add_argument("-i", "--image", required=True)
    parser.add_argument('-c', "--use-cvlib", action='store_true')
    parser.add_argument('-l', "--use-large-model", action='store_true')
    parser.add_argument('-t', "--threshold", default=0.5, type=float)
    args = parser.parse_args()
    
    detect_model = ('use_cvlib' if args.use_cvlib else 'default')
    model_type = ('large' if args.use_large_model else 'small')

    encodings_pickle = CONFIG[detect_model][model_type]
    print("Encodings pickle: {}".format(encodings_pickle))

    path_name_encodings = load_encodings(encodings_pickle)
    encodings = [x[-1] for x in path_name_encodings]

    image = fr.load_image_file(args.image)
    img = recoginize_face_in_image(
        image, path_name_encodings, encodings, args.threshold, args.use_cvlib,
        args.use_large_model)

    cv2.imshow("Face recognition", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

'''
python recognize_face.py -t 0.5 -i "test/img1.jpg"
python recognize_face.py -t 0.5 -i "test/img1.jpg" --use-large-model

python recognize_face.py -t 0.5 -i "test/img1.jpg" --use-cvlib
python recognize_face.py -t 0.5 -i "test/img1.jpg" --use-cvlib --use-large-model
'''
