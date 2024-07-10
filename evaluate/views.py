import cv2
from rest_framework.response import Response
from rest_framework.decorators import api_view

from evaluate.utils.exceptions import SegmentationException


from .utils.converters import convert_imageID_confidence_pairs_to_shoe_confidence
from .utils.cpp_service import evaluate_all_properties_CPP, evaluate_all_properties_no_classification_CPP
from .utils.image_processing import extract_shoe_info_from_image

DISPLAY_IMAGES = False



# Method to recalculate properties of all
@api_view(['POST'])
def all_properties(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required'}, status=400)

    try:
        extracted_shoe_image, sorted_classification_data = extract_shoe_info_from_image(image, DISPLAY_IMAGES=False)

        evaluate_all_properties_CPP(extracted_shoe_image, sorted_classification_data)


    except Exception as e:
        return Response({'error': f'Error processing image: {str(e)}'}, status=500)

    return Response({'message': 'Image processed successfully'}, status=200)



@api_view(['POST'])
def all_properties_no_classification(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image is required'}, status=400)
    try:
        extracted_shoe_image, sorted_classification_data, segmentation_succesful = extract_shoe_info_from_image(image, DISPLAY_IMAGES=False)

        imageID_confidence_pairs = evaluate_all_properties_no_classification_CPP(extracted_shoe_image)

        shoe_confidence_pairs = convert_imageID_confidence_pairs_to_shoe_confidence(imageID_confidence_pairs)

    except Exception as e:
        return Response({'error': f'Error processing image: {str(e)}'}, status=500)

    if not segmentation_succesful:
        return Response({
            'message': 'Image could not be segmented, but properties were calculated successfully for the provided image',
            'shoe_confidence_pairs': shoe_confidence_pairs
        }, status=200)
    return Response({
        'message': 'Image processed successfully',
        'shoe_confidence_pairs': shoe_confidence_pairs
    }, status=200)



@api_view(['POST'])
def evaluate_color(request):
    image = request.FILES.get('image')
    print(image)
    if not image:
        return Response({'error': 'Image is required'}, status=400)

    extracted_shoe_image, _, _ = extract_shoe_info_from_image(image, DISPLAY_IMAGES=False)


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

    return Response({'message': 'Image processed successfully'}, status=200)



@api_view(['POST'])
def evaluate_shoe_type(request):
    shoe_image = request.FILES.get('image')
    if not shoe_image:
        return Response({'error': 'Shoe type is required'}, status=400)

    try:
        _, sorted_classification_data = extract_shoe_info_from_image(shoe_image, DISPLAY_IMAGES=False)
    except Exception as e:
        return Response({'error': f'Error fetching shoe images: {str(e)}'}, status=500)

    return Response({
        'shoe_type': sorted_classification_data
    }, status=200)
