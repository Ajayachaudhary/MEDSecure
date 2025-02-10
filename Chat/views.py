from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.models import User
from .models import Mesaage, EncryptedImage
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from AES_ECC.main import encrypt_and_hide_key, extract_and_decrypt
from AES_ECC.ECC import curve, G
import os
import uuid

def room(request, user, send_to):
    loggedUser = request.user
    username = loggedUser.username

    if username != user:
        return render(request, 'chat/chat.html', {'status': 'error', 'message': 'Oops Error!'})

    is_staff = loggedUser.is_staff
    messages = Mesaage.objects.filter(
        Q(sender=loggedUser, receiver__username=send_to) |
        Q(sender__username=send_to, receiver=loggedUser)
    ).order_by('timestamp')

    # Add encrypted image path to each message
    for message in messages:
        try:
            encrypted_image = EncryptedImage.objects.get(id=message.chat_id)
            message.encrypted_image_path = encrypted_image.encrypted_image_path
        except EncryptedImage.DoesNotExist:
            message.encrypted_image_path = None

    other_user = messages.exclude(sender=loggedUser).first()

    if is_staff:
        users = User.objects.filter(is_staff=False)
        room_name = f'{user}_{send_to}'
        if other_user and other_user.sender.username != send_to:
            context = {
                'status': 'error',
                'messages': 'No Messages...',
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
            }
            return render(request, 'chat/chat.html', context)

        return render(request, 'chat/chat.html', {
            'messages': messages,
            'users': users,
            'current_user': user,
            'other_user_name': send_to,
            'room_name': room_name
        })
    else:
        users = User.objects.filter(is_staff=True)
        room_name = f'{send_to}_{user}'
        if other_user and other_user.sender.username != send_to:
            context = {
                'status': 'error',
                'messages': 'No Messages...',
                'users': users,
                'current_user': user,
                'other_user_name': send_to,
            }
            return render(request, 'chat/chat.html', context)

        return render(request, 'chat/chat.html', {
            'messages': messages,
            'users': users,
            'current_user': user,
            'other_user_name': send_to,
            'room_name': room_name
        })

def chat_template(request):
    user = request.user
    username = user.username
    is_staff = user.is_staff

    if is_staff:
        users = User.objects.filter(is_staff=False)
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

    return render(request, 'chat/chat.html', context)

@csrf_exempt
def encrypt_image(request):
    key = "9e3f1a6039b70ac853fb3949883c0cac"  # this is aes key generated from generate_AES_key() function in ECC.py, it should generate a new key every time for each image that is going to be sent
    private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855  # this private, public key should generate at registration time only for doctor. generation of this code is present in ECC.py
    public_key = (
        18978333441288833782926241136669041791189032080772352147125050398549113838242,
        4574019226635624308158902747633238879561901950062217090244646744259582877871
    )
    if request.method == 'POST':
        try:
            image_data = request.POST.get('image')  # Get Base64 string
            unique_id = request.POST.get('id')  # Get unique ID
            if not image_data:
                return JsonResponse({"error": "No image data received"}, status=400)

            # Split the Base64 header from actual image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # Extract image format (png, jpg, etc.)

            # Generate a unique name for the image
            unique_filename = f'chat_image_{uuid.uuid4()}.{ext}'

            # Decode Base64 and create Django ContentFile
            decoded_image = ContentFile(base64.b64decode(imgstr), name=unique_filename)
            print(f"Decoded image name: {decoded_image.name}")

            # Ensure the images directory exists
            images_dir = os.path.join(os.path.dirname(__file__), '../media/temp_img')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            print(f"Images directory: {images_dir}")

            # Save the decoded image to a temporary file
            image_path = os.path.join(images_dir, decoded_image.name)
            with open(image_path, 'wb') as f:
                f.write(decoded_image.read())
            print(f"Image saved at: {image_path}")

            # Ensure the encrypted images directory exists
            encrypted_images_dir = os.path.join(os.path.dirname(__file__), '../media/encrypted_images')
            if not os.path.exists(encrypted_images_dir):
                os.makedirs(encrypted_images_dir)
            print(f"Encrypted images directory: {encrypted_images_dir}")

            # Generate unique names for the encrypted and decrypted images
            encrypted_filename = f'{uuid.uuid4()}_encrypted.png'
            decrypted_filename = f'{uuid.uuid4()}_decrypted.png'

            # Encrypt the image
            encrypted_path, image_shape = encrypt_and_hide_key(
                image_path,
                key,
                public_key,
                curve,
                G,
                os.path.join(encrypted_images_dir, encrypted_filename)
            )
            print(f"Encrypted image saved at: {encrypted_path}")

            # Save the encrypted image to the database with a relative path
            relative_encrypted_path = f'encrypted_images/{encrypted_filename}'
            EncryptedImage.objects.create(
                id=unique_id,
                original_image_name=decoded_image.name,
                encrypted_image_path=relative_encrypted_path
            )
            # Decrypt the image (if needed)
            # decrypted_path = extract_and_decrypt(
            #     encrypted_path,
            #     private_key,
            #     curve,
            #     os.path.join(encrypted_images_dir, decrypted_filename)
            # )
            # print(f"Decrypted image saved at: {decrypted_path}")

            return JsonResponse({"success": True, "message": "Image processed successfully"})

        except Exception as e:
            print(f"Error: {e}")  # Print the error to the console
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def decrypt_image(request):
    print("Decrypting image...")
    if request.method == 'POST':
        private_key = 6938227033753900972488869560043356740747013013967433652901998425138991487855  # this private, public key should generate at registration time only for doctor. generation of this code is present in ECC.py
        encrypted_image_path = request.POST.get('encrypted_image_path')
        if not encrypted_image_path:
            return JsonResponse({"error": "No encrypted image path provided"}, status=400)

        try:
            # Decrypt the image
            encrypted_image_full_path = os.path.join(os.path.dirname(__file__), '../media/', encrypted_image_path)
            decrypted_filename = f'{uuid.uuid4()}_decrypted.png'
            decrypted_images_dir = os.path.join(os.path.dirname(__file__), '../media/decrypted_images')
            if not os.path.exists(decrypted_images_dir):
                os.makedirs(decrypted_images_dir)
            decrypted_path = extract_and_decrypt(
                encrypted_image_full_path,
                private_key,
                curve,
                os.path.join(decrypted_images_dir, decrypted_filename)
            )
            print(f"Decrypted image saved at: {decrypted_path}")
            relative_decrypted_path = f'decrypted_images/{decrypted_filename}'
            return JsonResponse({"decrypted_image_url": f'/media/{relative_decrypted_path}'})

        except Exception as e:
            print(f"Error: {e}")  # Print the error to the console
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
