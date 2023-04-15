from django.db import models


# Create your models here.
class Crypto(models.Model):
    name = models.CharField(max_length=15)
    image_url = models.ImageField(null=True, blank=True)
