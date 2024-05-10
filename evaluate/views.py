from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .utils.scraping import scrape_product_photos
from .models import ShoeMetadata

# Create your views here.
@api_view(['POST'])
def process_product_from_url(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        scrape_product_photos(url)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product processed successfully'}, status=200)
