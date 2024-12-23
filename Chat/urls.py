from django.urls import path
from . import views

urlpatterns = [
    path("<str:user>/<str:send_to>/", views.room, name="chat"),
    path("", views.chat_template, name="initial-chat"),
]
