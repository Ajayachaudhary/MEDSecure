from django.contrib import admin
from Chat.models import Mesaage

class MesaageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'image', 'timestamp')

admin.site.register(Mesaage, MesaageAdmin)
