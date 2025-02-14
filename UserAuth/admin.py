from django.contrib import admin
from .models import DoctorLicense

@admin.register(DoctorLicense)
class DoctorLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number',)
    search_fields = ('license_number',)
