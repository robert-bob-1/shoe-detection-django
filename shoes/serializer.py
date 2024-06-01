import base64
from rest_framework import serializers

from evaluate.models import ShoeMetadata, ShoeImage

class ShoeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShoeImage
        fields = ['id', 'image']

    def get_image(self, obj):
        with open(obj.image.path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class ShoeMetadataSerializer(serializers.ModelSerializer):
    images = ShoeImageSerializer(many=True, read_only=True)

    class Meta:
        model = ShoeMetadata
        fields = ['id', 'name', 'brand', 'price', 'url', 'images']
