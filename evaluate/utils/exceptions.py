class DuplicateProductException(Exception):
    def __init__(self, message):
        super().__init__(message)

class SegmentationException(Exception):
    def __init__(self, message):
        super().__init__("Product could not be segmented. Please try again by cropping on or out the image of the shoe pair, or by trying another image.")