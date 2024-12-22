from django.urls import path
from . import views

urlpatterns = [
    path("<str:user>/<str:send_to>/", views.chat, name="chat"),
]
