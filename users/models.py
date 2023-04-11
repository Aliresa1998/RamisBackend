from django.db import models

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User

from users.validators import validate_image_size


class CustomUser(models.Model):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True)
    image = models.ImageField(validators=[validate_image_size])
    country = models.CharField(max_length=50, validators=[
        MinLengthValidator(3)])
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
