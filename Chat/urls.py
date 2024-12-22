from django.urls import path
from . import views

urlpatterns = [
    path("<str:sender>/<str:receiver>/", views.chat, name="chat"),
]
