from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from Chat.models import Mesaage
from django.db.models import Q
from UserAuth.models import DoctorLicense, UserPublicKey
from AES_ECC.ECC import generate_private_key, generate_public_key
from django.core.cache import cache

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

@csrf_exempt
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
@csrf_exempt
def handle_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        doctor_license = request.POST.get('doctor_license')

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

        # If user is signing up as a doctor, verify their license
        if user_type == 'doctor':
            if not DoctorLicense.objects.filter(license_number=doctor_license).exists():
                messages.error(request, "Invalid doctor license. Please enter a valid license number.")
                return render(request, 'signup.html', {
                    'username': username,
                    'email': email,
                    'user_type': user_type,
                    'doctor_license': doctor_license,
                })

        # Create the user after validation
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)

            # If the user is a doctor, grant staff permissions
            if user_type == 'doctor':
                user.is_superuser = True
                user.is_staff = True

            user.save()

            # Generate private and public keys
            private_key = generate_private_key()
            public_key = generate_public_key(private_key)

            # Save the public key to the database
            UserPublicKey.objects.create(user=user, public_key=str(public_key))

            # Store the private key in the server cache
            cache.set(f'private_key_{user.id}', private_key, timeout=None)

            # Log in the user after signup
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {username}!")
            return redirect('home')  # Redirect to homepage or dashboard
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('signup')

    # If GET request, just render the signup page
    return render(request, 'signup.html')
