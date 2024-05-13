from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .utils.scraping import scrape_product_object, scrape_product_urls
from .models import ShoeMetadata

# Create your views here.
@api_view(['POST'])
def scrape_product(request):
    url = request.data.get('url')
    print(url)
    print(request.data)

    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        print(url)
        scrape_product_object(url)
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
