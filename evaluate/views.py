import cv2
from django.shortcuts import get_object_or_404
from matplotlib import pyplot as plt
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

from skimage.feature import hog
from skimage import exposure


from .utils.cpp_service import compute_CPP_properties_and_save
from .utils.database import save_image_classification_data, save_product_classification_data
from .utils.exceptions import DuplicateProductException
from .utils.image_processing import extract_shoe_info_from_image
from .utils.scraping import scrape_product_object_and_save, scrape_product_urls

DISPLAY_IMAGES = False

@api_view(['POST'])
def scrape_product(request):
    url = request.data.get('url')
    print(url)
    print(request.data)

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        shoe_metadata, shoe_images, shoe_images_ids = scrape_product_object_and_save(url)
    except Exception as e:
        return Response({'error': f'Error processing product: {str(e)}'}, status=500)

    try:
        all_classification_data = []
        for i in range(len(shoe_images)):
            try:

                extracted_shoe, sorted_classification_data = extract_shoe_info_from_image(
                    shoe_images[i],
                    DISPLAY_IMAGES= DISPLAY_IMAGES
                )
                save_image_classification_data(shoe_images_ids[i], sorted_classification_data)
                all_classification_data.append(sorted_classification_data)

                compute_CPP_properties_and_save(extracted_shoe, shoe_images_ids[i])
            except Exception as e:
                print(f'Error processing image: {str(e)}')
                continue

        save_product_classification_data(shoe_metadata, all_classification_data)

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
                shoe_metadata, shoe_images, shoe_images_ids = scrape_product_object_and_save(product_url)
            except DuplicateProductException as e:
                continue
            except Exception as e:
                return Response({'error': f'Error processing product: {str(e)}'}, status=500)

            for i in range(len(shoe_images)):
                try:
                    extracted_shoe, sorted_classification_data = extract_shoe_info_from_image(
                        shoe_images[i],
                        display_image= DISPLAY_IMAGES
                    )

                    compute_CPP_properties_and_save(extracted_shoe, shoe_images_ids[i])
                except Exception as e:
                    continue

    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product URLs scraped successfully'}, status=200)

# Method to recalculate properties of all

@api_view(['POST'])
def evaluate_color(request):
    image = request.FILES.get('image')
    print(image)
    if not image:
        return Response({'error': 'Image is required'}, status=400)

    extracted_shoe_image, sorted_classification_data = extract_shoe_info_from_image(image, DISPLAY_IMAGES=False)


    try:
        # # Send the extracted shoe image to the Evaluator API for further processing
        img_encoded = cv2.imencode('.jpg', extracted_shoe_image)[1].tostring()
        # multipart_form_data = {'file': ('shoe.jpg', img_encoded, 'image/jpeg')}

        # response = requests.post('http://localhost:8081/evaluate', files=multipart_form_data)

        # # print(response.json())

        # if response.status_code != 200:
        #     raise Exception(response.json())

    except Exception as e:
        return Response({'error': f'Error sending image to Evaluator API: {str(e)}'}, status=500)

    # # fetch received images and return a response containing the image data
    # try:
    #      # get the shoe image names corresponding to the shoe image id's in the response
    #     shoes = []
    #     for image_id in response.json()["shoeImageIds"]:
    #     #     shoe = ShoeImage.objects.get(id=image_id)
    #     #     print(shoe.image)

    #     #     shoes.append(shoe)
    #         shoe_image = get_object_or_404(ShoeImage, pk=image_id)
    #         shoe_data = ShoeImageAndMetadataSerializer(shoe_image).data
    #         shoes.append(shoe_data)

    #     page_number = request.GET.get('page', 1)
    #     page_size = request.GET.get('page_size', 4)

    #     paginator = Paginator(shoes, page_size)
    #     page = paginator.get_page(page_number)

    #     serialized_shoes = ShoeMetadataAndImageSerializer(page, many=True)
    #     # serialized_shoes = ShoeImageAndMetadataSerializer(page, many=True)
    # except Exception as e:
    #     return Response({'error': f'Error fetching shoe images: {str(e)}'}, status=500)

    # return Response({
    #     'shoes': serialized_shoes.data,
    #     'page': page.number,
    #     'pages': paginator.num_pages,
    #     'total': paginator.count
    # }, status=200)
    return Response({'message': 'Image processed successfully'}, status=200)


@api_view(['POST'])
def evaluate_shoe_type(request):
    shoe_image = request.FILES.get('image')
    if not shoe_image:
        return Response({'error': 'Shoe type is required'}, status=400)

    try:
        extracted_shoe, sorted_classification_data = extract_shoe_info_from_image(shoe_image, DISPLAY_IMAGES=False)
    except Exception as e:
        return Response({'error': f'Error fetching shoe images: {str(e)}'}, status=500)

    return Response({
        'shoe_type': sorted_classification_data
    }, status=200)
