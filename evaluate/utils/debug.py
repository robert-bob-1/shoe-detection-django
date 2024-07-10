import cv2


def display_image(image, window_name='Uploaded Image'):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, image.shape[1], image.shape[0])

    # Display the image using cv2.imshow
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
