from matplotlib import pyplot as plt
import numpy as np
from rest_framework.response import Response
from rest_framework.decorators import api_view
import cv2

from evaluate.utils.debug import display_image

from .utils.scraping import scrape_product_object, scrape_product_urls
from .models import ShoeMetadata

MODE = 'debug'

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

        if MODE == 'debug':
            display_image(img_cv2)

        # print(image)
        # plt.imshow(image)
        # # Read the image
        # img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # # Calculate blurriness
        # blur_score = cv2.Laplacian(img_cv2, cv2.CV_64F).var()

        # # Print the blurriness score
        # print(f"Blurriness score: {blur_score}")

        # import matplotlib.pyplot as plt
        # cv2.imshow('Image', img_cv2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # # Display the image
        # plt.imshow(img)
        # plt.axis('off')
        # plt.show()
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Image processed successfully'}, status=200)
