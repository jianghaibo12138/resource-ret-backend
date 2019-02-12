import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

django_logger = logging.getLogger("django")


class OrderService:

    def __init__(self):
        super(OrderService, self).__init__()

    def send_order_to_owner_channel(self, channel_name, message):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(channel_name, {
            "type": "send.message",
            "message": message
        })

    def send_order_to_washer_channel(self, owner_id, group_name, message):
        django_logger.info("[OrderService] owner id: {}, message: {}".format(owner_id, message))
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send.message",
                "message": message,
            },
        )
