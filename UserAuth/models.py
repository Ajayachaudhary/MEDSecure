from django.db import models
from django.contrib.auth.models import User

class DoctorLicense(models.Model):
    license_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.license_number

class UserPublicKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user.username}'s Public Key"
