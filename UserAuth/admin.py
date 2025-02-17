from django.contrib import admin
from .models import DoctorLicense, UserPublicKey

@admin.register(DoctorLicense)
class DoctorLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number',)
    search_fields = ('license_number',)

@admin.register(UserPublicKey)
class UserPublicKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'public_key')
    search_fields = ('user__username', 'public_key')
