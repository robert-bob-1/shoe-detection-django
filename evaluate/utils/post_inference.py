import cv2
import numpy as np


def extract_shoe(inference_results, cv_image, DISPLAY_IMAGES=True):
    # Extract mask
    masks = inference_results[0].masks

    # Extract the first mask pixel coordinates
    mask = masks.xy[0]

    # Create an empty mask image with the same dimensions as the input image
    mask_img = np.zeros(cv_image.shape[:2], dtype=np.uint8)

    # Convert mask coordinates to an appropriate format for fillPoly
    mask = np.array(mask, dtype=np.int32)

    # Fill the mask image with the detected mask
    cv2.fillPoly(mask_img, [mask], 255)

    if DISPLAY_IMAGES == True:
        cv2.imshow('mask', mask_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Extract the shoe from the image using the mask
    shoe_img = cv2.bitwise_and(cv_image, cv_image, mask=mask_img)
     # Create a white background image
    white_background = np.full(cv_image.shape, 255, dtype=np.uint8)

    # Use bitwise NOT to invert the mask, selecting the background
    inverted_mask = cv2.bitwise_not(mask_img)

    # Apply the inverted mask to the white background
    white_background = cv2.bitwise_and(white_background, white_background, mask=inverted_mask)

    # Combine the shoe with the white background
    shoe_img = cv2.bitwise_or(shoe_img, white_background)
    if DISPLAY_IMAGES == True:
        cv2.imshow('shoe', shoe_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    stretched_shoe = scale_shoe(shoe_img, mask_img)

    if DISPLAY_IMAGES == True:
        cv2.imshow('stretched shoe', stretched_shoe)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return stretched_shoe

def extract_classification_data(class_results):
    result = class_results[0]
    probabilities = result.probs

    class_names = []
    class_confidences = []
    # print(f"result.names = {result.names}")
    # Extract confidence scores for each class
    confidences = probabilities.data.cpu().numpy()
    for key, class_name in result.names.items():
        class_names.append(class_name)
        class_confidences.append(float(confidences[key]))

    classification_data = {class_name: confidence for class_name, confidence in zip(class_names, class_confidences)}
    # print(f"Classification data: {classification_data}")

    # Sort the classification data by confidence score
    sorted_classification_data = {k: v for k, v in sorted(classification_data.items(), key=lambda item: item[1], reverse=True)}
    print(f"Sorted classification data: {sorted_classification_data}")

    return sorted_classification_data

def scale_shoe(cv_image, mask_image):
    # Find the bounding box of the shoe mask
    contours, _ = cv2.findContours(mask_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x,y,w,h = cv2.boundingRect(contours[0])

     # Calculate scaling factors to fit width and height
    scale_x = cv_image.shape[1] / w
    scale_y = cv_image.shape[0] / h

    # Choose the smaller scaling factor to avoid cropping
    scale_factor = min(scale_x, scale_y)

    # Resize the shoe region
    stretched_shoe = cv2.resize(cv_image[y:y+h, x:x+w], None, fx=scale_factor, fy=scale_factor)

    # Create a white background image
    result_image = np.full(cv_image.shape, 255, dtype=np.uint8)

    # Calculate the y-offset to place the shoe at the bottom
    y_offset = result_image.shape[0] - stretched_shoe.shape[0]

    # Calculate x-offset to center horizontally
    x_offset = (result_image.shape[1] - stretched_shoe.shape[1]) // 2

    # Paste the stretched shoe onto the white background
    result_image[y_offset:y_offset + stretched_shoe.shape[0],
                 x_offset:x_offset + stretched_shoe.shape[1]] = stretched_shoe

    return result_image

