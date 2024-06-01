import numpy as np
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2
from ultralytics import YOLO
from django.db import transaction

from .utils.debug import display_image

from .utils.image_processing import shoe_detection_pipeline
from .utils.scraping import scrape_product_object_and_save, scrape_product_urls
from .models import ShoeImage, ShoeMetadata

DISPLAY_IMAGES = False

# Create your views here.

# @transaction.atomic
@api_view(['POST'])
def scrape_product(request):
    url = request.data.get('url')
    print(url)
    print(request.data)

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        shoe_metadata, shoe_images = scrape_product_object_and_save(url)
    except Exception as e:
        return Response({'error': f'Error processing product: {str(e)}'}, status=500)

    try:
        for image in shoe_images:
            extracted_shoe_img = shoe_detection_pipeline(image, DISPLAY_IMAGES)

            img_encoded = cv2.imencode('.jpg', extracted_shoe_img)[1].tostring()
            # multipart_form_data = {
            #     'file': ('shoe.jpg', img_encoded, 'image/jpeg')
            # }

            # response = requests.post(f'http://localhost:8081/compute-properties-and-save?id={shoe_metadata.id}', files=multipart_form_data)

            # if response.status_code != 200:
            #     raise Exception(response.json())

    except Exception as e:
        return Response({'error': f'Error sending product: {str(e)}'}, status=500)

    return Response({'message': 'Product processed successfully'}, status=200)

@api_view(['POST'])
def scrape_page(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        product_urls = scrape_product_urls(url)
        for product_url in product_urls:
            try:
                shoe_metadata, shoe_images = scrape_product_object_and_save(product_url)
            except Exception as e:
                return Response({'error': f'Error processing product: {str(e)}'}, status=500)

            # try:
            #     for image in shoe_images:
                    # extracted_shoe_img = shoe_detection_pipeline(image, DISPLAY_IMAGES)

                    # img_encoded = cv2.imencode('.jpg', extracted_shoe_img)[1].tostring()
                    # multipart_form_data = {
                    #     'file': ('shoe.jpg', img_encoded, 'image/jpeg')
                    # }

                    # response = requests.post(f'http://localhost:8081/compute-properties-and-save?id={shoe_metadata.id}', files=multipart_form_data)

                    # if response.status_code != 200:
                    #     raise Exception(response.json())

            # except Exception as e:
            #     return Response({'error': f'Error sending product: {str(e)}'}, status=500)


    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product URLs scraped successfully'}, status=200)


@api_view(['POST'])
def upload_image(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required'}, status=400)

    extracted_shoe_img = None
    try:
        extracted_shoe_img = shoe_detection_pipeline(image, DISPLAY_IMAGES)
    except Exception as e:
        return Response({'error': f'Error processing image: {str(e)}'}, status=500)

    try:
        # Send the extracted shoe image to the Evaluator API for further processing
        img_encoded = cv2.imencode('.jpg', extracted_shoe_img)[1].tostring()
        multipart_form_data = {'file': ('shoe.jpg', img_encoded, 'image/jpeg')}

        response = requests.post('http://localhost:8081/evaluate', files=multipart_form_data)

        if response.status_code != 200:
            raise Exception(response.json())

    except Exception as e:
        return Response({'error': f'Error sending image to Evaluator API: {str(e)}'}, status=500)

    return Response({'message': 'Image processed successfully'}, status=200)
