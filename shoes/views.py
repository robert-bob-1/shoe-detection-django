from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from evaluate.models import ShoeMetadata, ShoeImage

from evaluate.utils.serializer import ShoeImageSerializer, ShoeMetadataAndImagesSerializer

@api_view(['GET'])
def get_all(request):
    print(request)
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 4)

    shoes = ShoeMetadata.objects.all()
    paginator = Paginator(shoes, page_size)
    page = paginator.get_page(page_number)

    serialized_shoes = ShoeMetadataAndImagesSerializer(page, many=True)
    return Response({
        'shoes': serialized_shoes.data,
        'page': page.number,
        'pages': paginator.num_pages,
        'total': paginator.count
    }, status=200)

@api_view(['GET'])
def get_images(request):
    try:
        shoe_images = ShoeImage.objects.all()
        serialized_shoes = ShoeImageSerializer(shoe_images, many=True)
    except:
        return Response({'error': 'Error fetching shoe images'}, status=500)

    return Response({
        'shoes': serialized_shoes.data
    }, status=200)
