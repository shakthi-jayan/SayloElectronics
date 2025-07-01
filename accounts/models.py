from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField

class User(AbstractUser):
    # Existing fields
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Add new profile fields
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=(
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ), blank=True, null=True)
    country = CountryField(blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"