

import cv2
import numpy as np
from ultralytics import YOLO
from django.core.files.uploadedfile import InMemoryUploadedFile

from evaluate.utils.debug import display_image
from evaluate.utils.post_inference import extract_shoe

PATH_TO_MODEL = 'best-seg.pt'
SEGMENTATION_MODEL = YOLO(PATH_TO_MODEL)

def shoe_detection_pipeline(image, DISPLAY_IMAGES=False):
    numpy_image = None
    if isinstance(image, InMemoryUploadedFile):
        numpy_image = np.frombuffer(image.read(), np.uint8)
    else:
        numpy_image = np.frombuffer(image, np.uint8)
    # Read the image
    img_cv2 = cv2.imdecode(numpy_image, cv2.IMREAD_COLOR)

    if DISPLAY_IMAGES == True:
        display_image(img_cv2)

    # Calculate blurriness
    blur_score = cv2.Laplacian(img_cv2, cv2.CV_64F).var()

    # Print the blurriness score; it is inversely proportional to the sharpness of the image
    print(f"Blurriness score: {blur_score}")

    # If the image is too blurry end execution
    if blur_score < 100:
        raise Exception('Image is too blurry')

    # Run inference
    results = SEGMENTATION_MODEL(img_cv2, show=False, device=0)

    # Extract the shoe from the image
    extracted_shoe_img = extract_shoe(results, img_cv2, DISPLAY_IMAGES)

    return extracted_shoe_img