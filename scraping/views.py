from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from scraping.strategy.strategy_utils import get_scraping_strategy_from_url
from evaluate.models import Website

# Create your views here.

@api_view(['POST'])
def scrape_product(request):
    url = request.data.get('url')
    print(url)
    print(request.data)
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    try:
        scraping_strategy = get_scraping_strategy_from_url(url)
        scraping_strategy.scrape_product(url)
    except Exception as e:
        return Response({'error': f'Error scraping product: {str(e)}'}, status=500)

    return Response({'message': 'Product processed successfully'}, status=200)

@api_view(['POST'])
def scrape_page(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': 'URL is required'}, status=400)

    # page_number_url_suffix = request.data.get('page_number_url_suffix')
    page_interval_start = request.data.get('page_interval_start')
    page_interval_end = request.data.get('page_interval_end')

    if page_interval_start is None or page_interval_end is None:
        # page_number_url_suffix = ""
        page_interval_start = 1
        page_interval_end = 1

    try:
        scraping_strategy = get_scraping_strategy_from_url(url)
        scraping_strategy.scrape_pages(url, page_interval_start, page_interval_end)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Product URLs scraped successfully'}, status=200)

@api_view(['POST'])
def website_update(request):
    site_name = request.data.get('site_name')
    site_url = request.data.get('site_url')
    site_logo = request.data.get('site_logo')

    if not site_name or not site_url or not site_logo:
        return Response({'error': 'Site name, URL and logo are required'}, status=400)

    try:
        existing_website = Website.objects.get(name=site_name)

        if existing_website:
            existing_website.url = site_url
            existing_website.logo = site_logo
            existing_website.save()
    except Website.DoesNotExist:
        new_website = Website(name=site_name, url=site_url, logo=site_logo)
        new_website.save()
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({'message': 'Website updated successfully'}, status=200)
