from django.contrib import admin

from evaluate.models import ShoeClassification, ShoeDominantColor, ShoeImage, ShoeMetadata, ShoeProperties

# Register your models here.
admin.site.register(ShoeMetadata)
admin.site.register(ShoeImage)
admin.site.register(ShoeProperties)
admin.site.register(ShoeDominantColor)
admin.site.register(ShoeClassification)