import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Mesaage
from django.contrib.auth.models import User
import base64
from django.core.files.base import ContentFile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')
        receiver_username = data.get('receiver')

        # Save message to database
        await self.save_message(
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
                    "message": data.get('message'),
                    "sender": data.get('sender'),
                    "type": message_type
                }
            }
        )

    @database_sync_to_async
    def save_message(self, content, receiver_username, message_type='text'):
        try:
            receiver = User.objects.get(username=receiver_username)

            if message_type == 'image':
                # Handle image data
                format, imgstr = content.split(';base64,')
                ext = format.split('/')[-1]
                image_data = ContentFile(base64.b64decode(imgstr), name=f'chat_image.{ext}')

                Mesaage.objects.create(
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
