import cv2


def display_image(image):
    # Display the image using cv2.imshow
    cv2.imshow('Uploaded Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
