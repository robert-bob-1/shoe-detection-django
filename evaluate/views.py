from matplotlib import pyplot as plt
import numpy as np
from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2
from ultralytics import YOLO
import tensorflow as tf
import torch

from evaluate.utils.debug import display_image

from .utils.scraping import scrape_product_object, scrape_product_urls
from .models import ShoeMetadata

DISPLAY_IMAGES = True
PATH_TO_MODEL = 'best-seg.pt'
SEGMENTATION_MODEL = YOLO(PATH_TO_MODEL)


# Create your views here.
@api_view(['POST'])
def scrape_product(request):
    url = request.data.get('url')
    print(url)
    print(request.data)

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    shoeMetadata = None
    try:
        print(url)
        shoeMetadata = scrape_product_object(url)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    try:
        shoeMetadata.save()
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product processed successfully'}, status=200)

@api_view(['POST'])
def scrape_page(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        product_urls = scrape_product_urls(url)
        for product_url in product_urls:
            print(product_url)
            # scrape_product_photos(product_url)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product URLs scraped successfully'}, status=200)


@api_view(['POST'])
def upload_image(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required'}, status=400)

    try:
        # Read the image
        numpy_image = np.fromstring(image.read(), np.uint8)
        img_cv2 = cv2.imdecode(numpy_image, cv2.IMREAD_COLOR)

        # if DISPLAY_IMAGES == True:
        #     display_image(img_cv2)

        # Calculate blurriness
        # color_ = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        blur_score = cv2.Laplacian(img_cv2, cv2.CV_64F).var()

        # Print the blurriness score; it is inversely proportional to the sharpness of the image
        print(f"Blurriness score: {blur_score}")

        # Run inference
        results = SEGMENTATION_MODEL(img_cv2, show=False, device=0)

        # Extract mask
        masks = results[0].masks

        # Extract the first mask pixel coordinates
        mask = masks.xy[0]
        print(mask)

        # Create an empty mask image with the same dimensions as the input image
        mask_img = np.zeros(img_cv2.shape[:2], dtype=np.uint8)

        # Fill the mask image with the detected mask
        # for segment in mask:
        #     segment = np.array(segment, dtype=np.int32)
        #     cv2.fillPoly(mask_img, [segment], 255)

        # cv2.imshow('mask', mask_img)
        # cv2.waitKey(0)



    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Image processed successfully'}, status=200)
