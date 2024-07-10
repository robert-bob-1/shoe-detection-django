import base64
from rest_framework import serializers

from evaluate.models import ShoeMetadata, ShoeImage

class ShoeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShoeImage
        fields = ['id', 'image', 'image_local']

    def get_image(self, obj):
        with open(obj.image_local.path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class ShoeMetadataAndImagesSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)

    class Meta:
        model = ShoeMetadata
        fields = ['id', 'name', 'brand', 'price', 'url', 'images']

class ShoeMetadataAndImageSerializer(serializers.ModelSerializer):
    image = ShoeImageSerializer(read_only=True)

    class Meta:
        model = ShoeMetadata
        fields = ['id', 'name', 'brand', 'price', 'url', 'image']

class ShoeImageAndMetadataSerializer(serializers.ModelSerializer):
    shoe = ShoeMetadataAndImagesSerializer(read_only=True)  # Reuse existing ShoeMetadata serializer

    class Meta:
        model = ShoeImage
        fields = ['id', 'image', 'shoe']  # Include the image field