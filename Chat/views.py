from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Mesaage
from django.db.models import Q

def chat_with_user(request, username):
    # Get the logged-in user
    logged_user = request.user

    # Get the user to chat with
    other_user = get_object_or_404(User, username=username)

    # Fetch messages between the logged-in user and the selected user
    messages = Mesaage.objects.filter(
        (Q(sender=logged_user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=logged_user))
    ).order_by('timestamp')

    # Render the chat page with the fetched messages
    return render(request, 'chat_with_user.html', {
        'messages': messages,
        'logged_user': logged_user,
        'other_user': other_user,
    })
