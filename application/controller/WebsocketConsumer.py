import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from application.models import AuthUser, WebsocketChannel

django_logger = logging.getLogger("django")


# washer order information ws
class OwnerOrderConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        owner_id = self.scope['url_route']['kwargs']['owner_id']
        owner = AuthUser.objects.filter(id=owner_id).first()
        if not owner:
            await self.close()
        WebsocketChannel.objects.update_or_create(channel_name=self.channel_name, owner=owner)
        await self.accept()

    async def disconnect(self, close_code):
        WebsocketChannel.objects.filter(channel_name=self.channel_name, group_name="").delete()
        await self.close()

    async def receive_json(self, content, **kwargs):
        await self.channel_layer.send(self.channel_name, {
            "type": "send.message",
            "message": "Hello there!"
        })

    async def send_message(self, event):
        await self.send_json(content=event["message"])


# washer order information ws
class OwnerOrderGroupConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        owner_id = self.scope['url_route']['kwargs']['owner_id']
        owner = AuthUser.objects.filter(id=owner_id).first()
        if not owner:
            await self.close()
        WebsocketChannel.objects.update_or_create(channel_name=self.channel_name, owner=owner,
                                                  group_name=settings.CHANNEL_GROUP_TEMPLATE, is_group=True)
        await self.channel_layer.group_add(settings.CHANNEL_GROUP_TEMPLATE, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        WebsocketChannel.objects.filter(channel_name=self.channel_name,
                                        group_name=settings.CHANNEL_GROUP_TEMPLATE).delete()
        await self.channel_layer.group_discard(settings.CHANNEL_GROUP_TEMPLAT, self.channel_name)
        await self.close()

    async def receive_json(self, content, **kwargs):
        await self.channel_layer.group_send(settings.CHANNEL_GROUP_TEMPLATE, {
            "type": "send.message",
            "message": "Hello there!"
        })

    async def send_message(self, event):
        await self.send_json(content=event["message"])
