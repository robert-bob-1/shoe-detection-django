

import cv2
import numpy as np
from ultralytics import YOLO
from django.core.files.uploadedfile import InMemoryUploadedFile

from evaluate.utils.debug import display_image
from evaluate.utils.post_inference import extract_classification_data, extract_shoe

PATH_TO_SEG_MODEL = '../models/best-seg.pt'
SEGMENTATION_MODEL = YOLO(PATH_TO_SEG_MODEL)

class_names = ['boots', 'flip_flops', 'loafers', 'sandals', 'sneakers', 'soccer_shoes']



def extract_shoe_info_from_image(image, DISPLAY_IMAGES=True):
    try:
        cv2_image = from_InMemoryFile_to_cv2image(image, DISPLAY_IMAGES)

        extracted_shoe_img = segmented_shoe_from_cv2_image(cv2_image, DISPLAY_IMAGES)
        sorted_classification_data = shoe_class_from_cv2_image(cv2_image)

    except Exception as e:
        print(f'extract_shoe_info_from_image: {str(e)}')
        raise Exception(f'extract_shoe_info_from_image: {str(e)}')

    return extracted_shoe_img, sorted_classification_data




def segmented_shoe_from_cv2_image(cv2_image, DISPLAY_IMAGES=False):
    seg_results = SEGMENTATION_MODEL(cv2_image, show=False, device=0)
    # Extract the shoe from the image as cv2 image
    extracted_shoe_img = extract_shoe(seg_results, cv2_image, DISPLAY_IMAGES)

    return extracted_shoe_img

def shoe_class_from_cv2_image(img_cv2) -> list:
    # Compute the shoe class
    classification_model = YOLO('../models/yolov8-classification-last.pt')
    class_results = classification_model([img_cv2], show=True, save=False, device=0)

    # Extract the classification data
    sorted_classification_data = extract_classification_data(class_results)
    print(f"sorted_classification_data: {sorted_classification_data}")

    return sorted_classification_data

def from_InMemoryFile_to_cv2image(inMemoryUploadedFile, DISPLAY_IMAGES=True) -> np.ndarray:
    if inMemoryUploadedFile is None:
        raise Exception('No image provided')
    numpy_image = None
    if isinstance(inMemoryUploadedFile, InMemoryUploadedFile):
        numpy_image = np.frombuffer(inMemoryUploadedFile.read(), np.uint8)
    else:
        numpy_image = np.frombuffer(inMemoryUploadedFile, np.uint8)
    # Read the image
    img_cv2 = cv2.imdecode(numpy_image, cv2.IMREAD_COLOR)
    img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)

    if DISPLAY_IMAGES:
        display_image(img_cv2)

    return img_cv2





    # Calculate blurriness
    # blur_score = cv2.Laplacian(img_cv2, cv2.CV_64F).var()

    # # Print the blurriness score; it is inversely proportional to the sharpness of the image
    # print(f"Blurriness score: {blur_score}")

    # # If the image is too blurry end execution
    # if blur_score < 100:
    #     raise Exception('Image is too blurry')





    # # tensor_img = torch.from_numpy(extracted_shoe_img).permute(2, 0, 1).float().div(255.0).unsqueeze(0)
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # tensor_img = torch.from_numpy(extracted_shoe_img.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)

    # # Run inference for classification model
    # classification_results = CLASSIFICATION_MODEL(tensor_img)

    # # Get the predicted class probabilities (for the first/only image in the batch)
    # pred = classification_results[0].cpu().numpy()
    # predicted_class_index = np.argmax(pred)

    # # Get the class name and confidence score
    # predicted_class_name = class_names[predicted_class_index]
    # confidence_score = pred[predicted_class_index]

    # # Print the results
    # print(f"Predicted Class: {predicted_class_name}")
    # print(f"Confidence Score: {confidence_score:.2f}")

    # # test for not extracted image
    # tensor_img = torch.from_numpy(img_cv2.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
    # classification_results = CLASSIFICATION_MODEL(tensor_img)

    # pred = classification_results[0].cpu().numpy()
    # predicted_class_index = np.argmax(pred)
    # predicted_class_name = class_names[predicted_class_index]
    # confidence_score = pred[predicted_class_index]

    # print(f"Predicted Class: {predicted_class_name}")
    # print(f"Confidence Score: {confidence_score:.2f}")

    # # classification_results = CLASSIFICATION_MODEL([image])
    # classification_results.print()
    # classification_results.xyxy[0]  # img1 predictions (tensor)
    # classification_results.pandas().xyxy[0]  # img1 predictions (pandas)

    # # revert POSIX path fix
    # pathlib.PosixPath = temp