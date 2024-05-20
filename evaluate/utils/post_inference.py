import cv2
import numpy as np


def extract_shoe(inference_results, cv_image, DISPLAY_IMAGES=False):
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

    if DISPLAY_IMAGES == True:
        cv2.imshow('shoe', shoe_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return shoe_img