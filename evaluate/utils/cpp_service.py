
import cv2
import requests

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
