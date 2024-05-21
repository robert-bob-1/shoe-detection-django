from django.contrib import admin

from evaluate.models import ShoeImage, ShoeMetadata

# Register your models here.
admin.site.register(ShoeMetadata)
admin.site.register(ShoeImage)