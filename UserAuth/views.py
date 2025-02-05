from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from Chat.models import Mesaage
from django.db.models import Q
from AES_ECC.ECC import generate_private_key, generate_public_key
from django.core.cache import cache
from .models import UserProfile

@login_required(login_url="login")
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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('home')  # Redirect to a homepage or dashboard
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
        private_key = generate_private_key()
        public_key = generate_public_key(private_key)
        print("Private Key: ", private_key)
        print("Public Key: ", public_key)

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

            # Save public key in the UserProfile model
            UserProfile.objects.create(user=user, public_key=str(public_key))

            # Save private key in the server cache
            cache.set(f'private_key_{user.id}', private_key)

            # Log in the user after signup
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {username}!")
            return redirect('home')  # Redirect to a homepage or dashboard
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('signup')

    # If GET request, just render the signup page
    return render(request, 'signup.html')

@login_required(login_url="login")
def retrieve_private_key(request):
    user_id = request.user.id
    private_key = cache.get(f'private_key_{user_id}')
    if private_key:
        return render(request, 'display_key.html', {'private_key': private_key})
    else:
        messages.error(request, "Private key not found.")
        return redirect('home')
