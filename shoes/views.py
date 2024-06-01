from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from evaluate.models import ShoeMetadata, ShoeImage

from shoes.serializer import ShoeMetadataSerializer

@api_view(['GET'])
def get_all(requests):
    shoes = ShoeMetadata.objects.all()
    serialized_shoes = ShoeMetadataSerializer(shoes, many=True)

    for shoe in serialized_shoes.data:
        for image in shoe['images']:
            image_data = ShoeImage.objects.get(id=image['id']).image.read()
            shoe['images'] = image_data

    return Response(serialized_shoes.data, status=200)