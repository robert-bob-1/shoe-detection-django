from django.contrib import admin

from evaluate.models import ShoeClassification, ShoeDominantColor, ShoeHOG, ShoeHistograms, ShoeImage, ShoeLBP, ShoeMetadata, ShoeProperties, Website

# Register your models here.
admin.site.register(Website)
admin.site.register(ShoeMetadata)
admin.site.register(ShoeImage)
admin.site.register(ShoeProperties)
admin.site.register(ShoeDominantColor)
admin.site.register(ShoeClassification)
admin.site.register(ShoeHistograms)
admin.site.register(ShoeLBP)
admin.site.register(ShoeHOG)