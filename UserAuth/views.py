from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from Chat.models import Mesaage
from django.db.models import Q

@login_required( login_url="login")
def index(request):
    return redirect('chat/')

@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def login_view(request):
    return render(request, 'login.html')

@user_passes_test(lambda user: not user.is_authenticated, login_url='home')
def signup_view(request):
    return render(request, 'signup.html')

def handle_logout(request):
    # Log out the user
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')  # Redirect to the login page or any page you prefer

def handle_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('home')  # Redirect to a home page or dashboard
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('handle-login')  # Redirect back to login page for retry

    # If GET request, just render the login page
    return render(request, 'login.html')


def handle_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate form inputs
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Log in the user after signup
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {username}!")
            return redirect('home')  # Redirect to a homepage or dashboard
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('signup')

    # If GET request, just render the signup page
    return render(request, 'signup.html')
