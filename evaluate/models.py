from django.db import models

# Create your models here.

class ShoeMetadata(models.Model):
    name = models.CharField(max_length=100)
    images = models.ImageField(upload_to='shoe_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name


