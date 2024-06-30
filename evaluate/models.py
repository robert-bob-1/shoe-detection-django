from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

# Create your models here.

class Website(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    url = models.URLField(unique=True)
    logo = models.BinaryField()

    def __str__(self):
        return self.name

class ShoeMetadata(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=30, default='Brand')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField(unique=True)
    website = models.ForeignKey(Website, on_delete=models.CASCADE, default=1)
    classification = models.CharField(max_length=30, default='Unknown')
    classification_confidence = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class ShoeImage(models.Model):
    shoe = models.ForeignKey(ShoeMetadata, on_delete=models.CASCADE, related_name='images')
    image_local = models.ImageField(upload_to='shoe_images/')
    image = models.BinaryField()

    def __str__(self):
        return self.shoe.name

    @receiver(post_delete)
    def delete_image_file(sender, instance, **kwargs):
        if isinstance(instance, ShoeImage):
            default_storage.delete(instance.image_local.name)

class ShoeProperties(models.Model):
    shoe_image = models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    percentage_red = models.FloatField()
    percentage_green = models.FloatField()
    percentage_blue = models.FloatField()

    def __str__(self):
        return self.shoe_image.shoe.name

class ShoeDominantColor(models.Model):
    shoe_image = models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    frequency_percentage = models.FloatField()
    red = models.IntegerField()
    green = models.IntegerField()
    blue = models.IntegerField()

    def __str__(self):
        return self.shoe_image.shoe.name

class ShoeClassification(models.Model):
    shoe_image= models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    boots_confidence = models.FloatField()
    flip_flops_confidence = models.FloatField()
    loafers_confidence = models.FloatField()
    sandals_confidence = models.FloatField()
    sneakers_confidence = models.FloatField()
    soccer_shoes_confidence = models.FloatField()

    def __str__(self):
        return self.shoe_image.shoe.name


class ShoeHistograms(models.Model):
    shoe_image = models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    red_histogram = models.BinaryField()
    green_histogram = models.BinaryField()
    blue_histogram = models.BinaryField()

    def __str__(self):
        return f"RGB histograms for {self.shoe_image.shoe.name}"

class ShoeLBP(models.Model):
    shoe_image = models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    lbp_histogram = models.BinaryField()
    lbp_rows = models.IntegerField()
    lbp_columns = models.IntegerField()

    def __str__(self):
        return f"LBP histogram for {self.shoe_image.shoe.name}"

class ShoeHOG(models.Model):
    shoe_image = models.ForeignKey(ShoeImage, on_delete=models.CASCADE)
    hog_descriptor = models.BinaryField()
    hog_rows = models.IntegerField()
    hog_columns = models.IntegerField()

    def __str__(self):
        return f"HOG histogram for {self.shoe_image.shoe.name}"
