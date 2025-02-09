from django.contrib import admin
from Chat.models import Mesaage, EncryptedImage

class MesaageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'image', 'timestamp', 'chat_id')

class EncryptedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_image_name', 'encrypted_image_path', 'created_at')

admin.site.register(Mesaage, MesaageAdmin)
admin.site.register(EncryptedImage, EncryptedImageAdmin)
