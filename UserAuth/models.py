from django.db import models

class DoctorLicense(models.Model):
    license_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.license_number
