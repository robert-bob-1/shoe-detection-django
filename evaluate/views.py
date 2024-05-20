from tkinter import Image
from matplotlib import pyplot as plt
import numpy as np
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2
from ultralytics import YOLO
import tensorflow as tf
import torch

from evaluate.utils.debug import display_image
from evaluate.utils.post_inference import extract_shoe

from .utils.scraping import scrape_product_object, scrape_product_urls
from .models import ShoeMetadata

DISPLAY_IMAGES = False
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

        # Send the extracted shoe image to the Evaluator API for further processing
        img_encoded = cv2.imencode('.jpg', extracted_shoe_img)[1].tostring()
        # test show encoded image

        multipart_form_data = {'file': ('shoe.jpg', img_encoded, 'image/jpeg')}
        # encoded_test_img = cv2.imencode('.jpg', img_cv2)[1].tostring()
        # multipart_form_data = {'file': ('shoe.jpg', encoded_test_img, 'image/jpeg')}

        print('Sending image to evaluator API')
        response = requests.post('http://localhost:8081/evaluate', files=multipart_form_data)

        if response.status_code != 200:
            raise Exception(response.json())

    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Image processed successfully'}, status=200)
