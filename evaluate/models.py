from django.db import models

# Create your models here.

class ShoeMetadata(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()

    def __str__(self):
        return self.name

class ShoeImage(models.Model):
    shoe = models.ForeignKey(ShoeMetadata, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):
        return self.shoe.name
