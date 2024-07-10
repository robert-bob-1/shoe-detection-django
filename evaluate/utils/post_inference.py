import cv2
import numpy as np

from evaluate.utils.debug import display_image
from evaluate.utils.exceptions import SegmentationException


def extract_shoe(inference_results, cv_image, DISPLAY_IMAGES=False):
    # Extract mask
    masks = inference_results[0].masks

    # Extract the first mask pixel coordinates
    if masks == None:
        return cv_image
        # raise SegmentationException("Product could not be segmented. Please try again by cropping on or out the image of the shoe pair, or by trying another image.")

    mask = masks.xy[0]

    print(f"Mask shape: {mask.shape}")
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
    # Rotate the shoe image to be generally parallel to the x axis
    rotated_cv2_image, rotated_mask = rotate_image(cv_image, mask_image)

    # Find the bounding box of the shoe mask
    contours, _ = cv2.findContours(rotated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x,y,w,h = cv2.boundingRect(contours[0])
    print(f"Bounding box coordinates: {x} {y} {w} {h}")
     # Calculate scaling factors to fit width and height
    scale_x = rotated_cv2_image.shape[1] / w
    scale_y = rotated_cv2_image.shape[0] / h

    # Test display the rectangle
    box = cv2.boxPoints(((x + w // 2, y + h // 2), (w, h), 0))
    box = np.int0(box)
    cv2.drawContours(rotated_cv2_image, [box], 0, (0, 0, 255), 2)
    # display_image(rotated_cv2_image, 'Bounding rectangle')

    # Choose the smaller scaling factor to avoid cropping
    scale_factor = min(scale_x, scale_y)

    # We need a stretched shoe image to fit in the found location at the bottom of the image
    stretched_shoe = cv2.resize(rotated_cv2_image[y:y+h, x:x+w], None, fx=scale_factor, fy=scale_factor)
    # display_image(stretched_shoe, 'Stretched shoe')

    # Create a white background image to paste the stretched image over
    result_image = np.full(rotated_cv2_image.shape, 255, dtype=np.uint8)

    # Calculate the y-offset to place the shoe at the bottom
    y_offset = result_image.shape[0] - stretched_shoe.shape[0]

    # Calculate x-offset to center horizontally
    x_offset = (result_image.shape[1] - stretched_shoe.shape[1]) // 2

    # Paste the stretched shoe onto the white background
    # This basically fills the area selected by y_offset, x_offset and the edges of the image (which are the shape of the stretched shoe) with the stretched shoe
    # This provides a standardization to all shoe images and is essential for uniform histogram and features calculation
    result_image[y_offset:y_offset + stretched_shoe.shape[0],
                 x_offset:x_offset + stretched_shoe.shape[1]] = stretched_shoe

    # display_image(result_image)
    return result_image

def rotate_image(cv2_image, mask_image):
    # Mask is grayscale already, no need to convert it

    # Find contours for the shoe
    contours, _ = cv2.findContours(mask_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the minimum area rectangle that encapsules the contour
    # This gives us an idea of how to rotate the shoe
    # This method may be more damaging than helpful when the shoe is not segmented properly
    rect = cv2.minAreaRect(largest_contour)

    # Test display the rectangle
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2_image_clone = cv2_image.copy()
    cv2.drawContours(cv2_image_clone, [box], 0, (0, 0, 255), 2)
    # display_image(cv2_image_clone, 'Rotated rectangle')

    # Check if scale of the shoe needs to be adjusted so that it doesn't cut into the sides after rotation
    # For this we check if the shoe is wider than the image width, given we have the width of the minSizeRect
    # rect[1] is the w and h of rectangle
    print(f"Shoe width: {rect[1][0]} Shoe height: {rect[1][1]}")
    print(f"Image width: {cv2_image.shape[1]}")
    # not ideal for shoes that are naturally higher than they are wide (boots)
    # but considering the db shoes are processed through this as well this shouldn't be too big of an issue.
    shoe_length = rect[1][0] if rect[1][0] > rect[1][1] else rect[1][1]

    if shoe_length > cv2_image.shape[1]:
        # Find the scale factor
        scale = cv2_image.shape[1] / shoe_length
        print(f"Scaling by: {scale}")

        # Resize the images to fix cropping issues after rotation
        cv2_image = cv2.resize(cv2_image, (int(cv2_image.shape[1] * scale), int(cv2_image.shape[0] * scale)))
        mask_image = cv2.resize(mask_image, (int(mask_image.shape[1] * scale), int(mask_image.shape[0] * scale)))
        # display_image(cv2_image, "scaled down image")

    # Get the center of the shoe
    (center_x, center_y) = rect[0]
    # print(f"Shoe center coordinates: {center_x} {center_y}")

    width, height = cv2_image.shape[:2]

    # Move shoe to the center of the image to reduce chances of cropping

    # Calculate translation to center the shoe rectangle calculated above
    image_center_x = cv2_image.shape[1] // 2
    image_center_y = cv2_image.shape[0] // 2

    # Calculate the final translation location for each axis
    translate_x = image_center_x - center_x
    translate_y = image_center_y - center_y

    # Create the translation matrix
    # The translation matrix is a 2x3 matrix that defines how to move the image
    # The first row defines how the image shifts horizontally
    #     the [1, 0] mean that the new coordinate for each pixel is calculated like:
    #         1*oldX + 0*oldY
    #     and then the translation is added
    # Similar for the second row, the oldX is set to 0, the oldY is added,
    #   and the translation is added over it
    translation_matrix = np.float32([[1, 0, translate_x],
                                     [0, 1, translate_y]])

    # Apply translation rules defined above to both the mask and the image
    # Set border mode to replicate existing white background to not leave black pixels where image is translated
    # Mask is already black so it the default behaviour is fine
    translated_cv2_image = cv2.warpAffine(cv2_image, translation_matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    translated_mask = cv2.warpAffine(mask_image, translation_matrix, (width, height))
    # display_image(translated_cv2_image, 'Translated Image')
    # display_image(translated_mask, 'Translated Mask')


    # Get the angle of the shoe
    angle = rect[2]
    print(f"Shoe angle: {angle}")
    # There are two cases for the angles here, because of how minAreaRect works
    # The angles are defined only in the (0, 90) range, so we need to adjust the rotation to be negative in some cases:
    # If shoe width  < shoe height we need to subtract 90 degrees from the angle
    # If shoe height > shoe width  we leave the angle as it is
    #   other way to visualize:
    #   if the shoe is pointed to the 2nd or 4th quadrant, we leave the angle as it is
    #   if the shoe is pointed to the 1st or 3rd quadrant, we subtract 90 degrees
    if rect[1][0] < rect[1][1]:
        angle -= 90
    print(f"Adjusted shoe angle: {angle}")
    # Rotate the image
    translated_center = (image_center_x, image_center_y)
    rotation_matrix = cv2.getRotationMatrix2D(translated_center, angle, 1.0)

    rotated_cv2_image = cv2.warpAffine(translated_cv2_image, rotation_matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    rotated_mask = cv2.warpAffine(translated_mask, rotation_matrix, (width, height))

    # display_image(rotated_cv2_image, 'Rotated Image')
    # display_image(rotated_mask, 'Rotated Mask')

    return rotated_cv2_image, rotated_mask
