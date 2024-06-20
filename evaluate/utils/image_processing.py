

import cv2
import numpy as np
from ultralytics import YOLO
from django.core.files.uploadedfile import InMemoryUploadedFile

from evaluate.utils.debug import display_image
from evaluate.utils.post_inference import extract_classification_data, extract_shoe

PATH_TO_SEG_MODEL = '../models/best-seg.pt'
SEGMENTATION_MODEL = YOLO(PATH_TO_SEG_MODEL)

class_names = ['boots', 'flip_flops', 'loafers', 'sandals', 'sneakers', 'soccer_shoes']



def extract_shoe_info_from_image(image, DISPLAY_IMAGES=False):
    try:
        cv2_image = from_InMemoryFile_to_cv2image(image, DISPLAY_IMAGES)
        extracted_shoe_img = segmented_shoe_from_cv2_image(cv2_image, DISPLAY_IMAGES)
        sorted_classification_data = shoe_class_from_cv2_image(cv2_image)

    except Exception as e:
        print(f'extract_shoe_info_from_image: {str(e)}')
        raise Exception(f'extract_shoe_info_from_image: {str(e)}')

    return extracted_shoe_img, sorted_classification_data



def segmented_shoe_from_cv2_image(cv2_image, DISPLAY_IMAGES=False):
    seg_results = SEGMENTATION_MODEL(cv2_image, show=DISPLAY_IMAGES, device=0)
    # Extract the shoe from the image as cv2 image
    extracted_shoe_img = extract_shoe(seg_results, cv2_image, DISPLAY_IMAGES)
    # print("extracted_shoe_img size: ", extracted_shoe_img.shape)

    return extracted_shoe_img

def shoe_class_from_cv2_image(img_cv2) -> list:
    # Compute the shoe class
    classification_model = YOLO('../models/yolov8-classification-last.pt')
    class_results = classification_model([img_cv2], save=False, device=0)

    # Extract the classification data
    sorted_classification_data = extract_classification_data(class_results)
    # print(f"sorted_classification_data: {sorted_classification_data}")

    return sorted_classification_data

def from_InMemoryFile_to_cv2image(inMemoryUploadedFile, DISPLAY_IMAGES=False) -> np.ndarray:
    if inMemoryUploadedFile is None:
        raise Exception('No image provided')
    numpy_image = None
    if isinstance(inMemoryUploadedFile, InMemoryUploadedFile):
        numpy_image = np.frombuffer(inMemoryUploadedFile.read(), np.uint8)
    else:
        numpy_image = np.frombuffer(inMemoryUploadedFile, np.uint8)
    # Read the image
    img_cv2 = cv2.imdecode(numpy_image, cv2.IMREAD_COLOR)
    # Resize the image to 640x640 as thats the model input size
    img_cv2 = cv2.resize(img_cv2, (640, 640))

    if DISPLAY_IMAGES:
        display_image(img_cv2)

    return img_cv2
