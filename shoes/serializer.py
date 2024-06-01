from rest_framework import serializers
from evaluate.models import ShoeMetadata, ShoeImage

class ShoeImageSerializer(serializers.ModelSerializer):
    image = serializers.FileField()

    class Meta:
        model = ShoeImage
        fields = ['id', 'image']

class ShoeMetadataSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)

    class Meta:
        model = ShoeMetadata
        fields = ['id', 'name', 'price', 'url', 'images']
