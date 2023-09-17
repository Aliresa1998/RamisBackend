from django.db import models

from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from numpy import identity

from users.validators import validate_image_size


class Plan(models.Model):
    plan = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    is_delete = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.plan


class CustomUser(models.Model):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=50, validators=[
        MinLengthValidator(3)], null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True)
    national_code = models.CharField(null=True, blank=True, max_length=15)
    email = models.CharField(null=True, blank=True, max_length=250)
    is_admin = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, null=True, blank=True)


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sender_messages')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipient_messages', null=True, blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    send_all = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.subject

    class Meta:
        ordering = ['-created_at']


class Ticket(models.Model):
    STATUS_CHOISES = (
        ('close', 'close'),
        ('open', 'open')
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sender_ticket')
    receiver = models.CharField(null=True, blank=True, max_length=30)
    subject = models.CharField(null=True, blank=True, max_length=50)
    body = ArrayField(models.CharField(), blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOISES, default='open')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class Document(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='document')
    profile_image = models.ImageField(
        validators=[validate_image_size], null=True, blank=True)
    identity_card = models.ImageField(
        validators=[validate_image_size], null=True, blank=True)
    birth_certificate = models.ImageField(
        validators=[validate_image_size], null=True, blank=True)
    Commitment_letter = models.ImageField(
        validators=[validate_image_size], null=True, blank=True)
