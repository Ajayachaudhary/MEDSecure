import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Mesaage
from django.contrib.auth.models import User
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    # Class variable to track connected users
    connected_users = set()

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        # Add user to connected users set
        ChatConsumer.connected_users.add(self.user.username)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Broadcast updated user list to all connected clients
        await self.broadcast_user_status()

    async def disconnect(self, close_code):
        # Remove user from connected users set
        ChatConsumer.connected_users.discard(self.user.username)

        # Broadcast updated user list
        await self.broadcast_user_status()

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def broadcast_user_status(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_list",
                "connected_users": list(ChatConsumer.connected_users)
            }
        )

    async def user_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_list",
            "connected_users": event["connected_users"]
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')
        receiver_username = data.get('receiver')
        unique_id = data.get('id', 'id')  # Get the unique ID or generate a new one

        # Save message to database
        await self.save_message(
            unique_id=unique_id,
            content=data.get('message'),
            receiver_username=receiver_username,
            message_type=message_type
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": {
                    "id": unique_id,
                    "message": data.get('message'),
                    "sender": data.get('sender'),
                    "type": message_type
                }
            }
        )

    @database_sync_to_async
    def save_message(self, unique_id, content, receiver_username, message_type='text'):
        try:
            receiver = User.objects.get(username=receiver_username)

            if message_type == 'image':
                # Handle image data
                format, imgstr = content.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f'chat_image.{ext}')

                Mesaage.objects.create(
                    chat_id=unique_id,
                    sender=self.user,
                    receiver=receiver,
                    image=image_data
                )
            else:
                # Handle text message
                Mesaage.objects.create(
                    sender=self.user,
                    receiver=receiver,
                    content=content
                )

        except User.DoesNotExist:
            print(f"Receiver {receiver_username} not found")
        except Exception as e:
            print(f"Error saving message: {str(e)}")

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
