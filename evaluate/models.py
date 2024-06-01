from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

# Create your models here.

class ShoeMetadata(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

class ShoeImage(models.Model):
    shoe = models.ForeignKey(ShoeMetadata, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='shoe_images/')

    def __str__(self):
        return self.shoe.name

    @receiver(post_delete)
    def delete_image_file(sender, instance, **kwargs):
        if isinstance(instance, ShoeImage):
            default_storage.delete(instance.image.name)

class ShoeProperties(models.Model):
    shoe = models.ForeignKey(ShoeMetadata, on_delete=models.CASCADE)
    percentage_red = models.FloatField()
    percentage_green = models.FloatField()
    percentage_blue = models.FloatField()

    def __str__(self):
        return self.shoe.name
