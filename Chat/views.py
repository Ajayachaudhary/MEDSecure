from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Mesaage
from django.db.models import Q

def room(request, user, send_to):
    loggedUser = request.user
    username = loggedUser.username

    if username != user:
        return render( request, 'chat/chat.html', {'status': 'error', 'message': 'Opps Error!'} )

    is_staff = loggedUser.is_staff
    messages = Mesaage.objects.filter(
            Q(sender=loggedUser, receiver__username=send_to) |
            Q(sender__username=send_to, receiver=loggedUser)
        ).order_by('timestamp')
    other_user = messages.exclude(sender=loggedUser).first()

    if is_staff:
        users = User.objects.filter( is_staff=False )
        room_name = f'{user}_{send_to}'
        if other_user and other_user.sender.username != send_to:
            context = {
                'status': 'error',
                'messages': 'No Messages...',
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
            }
            return render( request, 'chat/chat.html', context )

        return render( request, 'chat/chat.html', {
                'messages': messages,
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
                'room_name': room_name
            } )
    else:
        users = User.objects.filter( is_staff=True )
        room_name = f'{send_to}_{user}'
        if other_user and other_user.sender.username != send_to:
            context = {
                'status': 'error',
                'messages': 'No Messages...',
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
            }
            return render( request, 'chat/chat.html', context )

        return render( request, 'chat/chat.html', {
                'messages': messages,
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
                'room_name': room_name
            } )

def chat_template(request):
    user = request.user
    username = user.username
    is_staff = user.is_staff

    if is_staff:
        users = User.objects.filter( is_staff = False)
        context = {
            'status': 'initial',
            'users': users,
            'current_user': username
        }
    else:
        users = User.objects.filter(is_staff=True)
        context = {
            'status': 'initial',
            'users': users,
            'current_user': username
        }

    return render( request, 'chat/chat.html', context )
