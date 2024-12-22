from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Mesaage
from django.db.models import Q

def chat(request, sender, receiver):
	user_id = request.user
	messages = Mesaage.objects.filter(Q(sender=user_id) | Q(receiver_id=user_id)).order_by('timestamp')
	return render(request, "chat/chat.html", {'messages': messages, 'logged_user_name': sender, 'other_user_name': receiver})
