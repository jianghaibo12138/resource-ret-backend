from django.urls import path

from application.controller.WebsocketConsumer import OwnerOrderConsumer, OwnerOrderGroupConsumer

websocket_urlpatterns = [
    path('ws-order-received/<str:owner_id>', OwnerOrderConsumer),
    path('ws-order-will-receive/<str:owner_id>', OwnerOrderGroupConsumer),
]