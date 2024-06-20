
import json
import cv2
import requests

from evaluate.utils.debug import display_image

def compute_CPP_properties_and_save(extracted_shoe_img, shoe_image_id):
    try:
        img_encoded = cv2.imencode('.jpg', extracted_shoe_img)[1].tostring()
        multipart_form_data = {
            'file': ('shoe.jpg', img_encoded, 'image/jpeg')
        }

        response = requests.post(f'http://localhost:8081/compute-properties-and-save?id={shoe_image_id}', files=multipart_form_data)

        if response.status_code != 200:
            raise Exception(response.json())
    except Exception as e:
        print(f'Error sending product: {str(e)}')
        raise Exception(f'Error sending product: {str(e)}')

def evaluate_all_properties_CPP(extracted_shoe_image, sorted_classification_data):
    try:
        img_encoded = cv2.imencode('.jpg', extracted_shoe_image)[1].tostring()
        multipart_form_data = {'file': ('shoe.jpg', img_encoded, 'image/jpeg')}

        # Convert the dictionary to a JSON string
        classification_json = json.dumps(sorted_classification_data)

        response = requests.post('http://localhost:8081/evaluate/all-properties', files=multipart_form_data, data={'classification_data': classification_json})

        if response.status_code != 200:
            raise Exception(response.json())
    except Exception as e:
        print(f'Error sending image to Evaluator API: {str(e)}')
        raise Exception(f'Error sending image to Evaluator API: {str(e)}')


def evaluate_all_properties_no_classification_CPP(extracted_shoe_image):
    try:
        img_encoded = cv2.imencode('.jpg', extracted_shoe_image)[1].tostring()
        multipart_form_data = {'file': ('shoe.jpg', img_encoded, 'image/jpeg')}

        response = requests.post('http://localhost:8081/evaluate', files=multipart_form_data)

        if response.status_code != 200:
            raise Exception(response.json())
    except Exception as e:
        print(f'Error sending image to Evaluator API: {str(e)}')
        raise Exception(f'Error sending image to Evaluator API: {str(e)}')