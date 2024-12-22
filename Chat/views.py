from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Mesaage
from django.db.models import Q

def chat(request, user, send_to):
	user_id = request.user

	if user_id.username != user:
		return render(request, 'chat/chat.html', {'status': 'error', 'message': 'Opps Error!'})
	messages = Mesaage.objects.filter(Q(sender=user_id) | Q(receiver_id=user_id)).order_by('timestamp')
	other_user = messages.exclude(sender=user_id).first()
	if other_user and other_user.sender.username != send_to:
		return render(request, 'chat/chat.html', {'status': 'error', 'message': 'Opps Error!'})

	return render(request, "chat/chat.html", {'messages': messages, 'logged_user_name': user, 'other_user_name': send_to})
