import logging
import os

import requests
from celery import Celery, Task
from django.urls import reverse

from application.services import OrderService
from resources import settings
from resources.payment.Alipay import Alipay

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resources.settings')

app = Celery('resources')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

order_service = OrderService()

if settings.DEBUG:
    HOST = settings.DEV_HOST
else:
    HOST = settings.PRD_HOST

pay_logger = logging.getLogger("pay")

@app.task(bind=True, max_retries=3)
def order_send_to_receive_queue(self, a, b):
    print('Request: {0!r}'.format(self.request))
    return a + b


@app.task(bind=True, max_retries=3)
def send_verify_code(self, tel_phone, verify_code):
    print(tel_phone, verify_code)


@app.task(bind=True, max_retries=3)
def pay_for_order(self, group_name, order, pay_way, owner_id):
    reverse_url = reverse(viewname="order:order-payed")
    request_url = "{}{}".format(HOST, reverse_url)
    if pay_way == "alipay":
        alipay_client = Alipay(appid=settings.ALIPAY_KEYS.get("app_id"),
                               app_private_key_path=settings.ALIPAY_KEYS.get('rsa_private_key'),
                               alipay_public_key_path=settings.ALIPAY_KEYS.get('rsa_public_key'), debug=settings.DEBUG)
        pay_result = alipay_client.alipay_trade_create(total_amount=order.get('price'), out_trade_no=order.get("id"),
                                                       subject=order.get('desc'), **order)
        if settings.DEBUG:
            pay_result = {
                "api_name": "alipay_trade_create_response",
                "code": "10000",
                "message": "Success",
                "out_trade_no": "a00425f7b0ac431cbc2fed0012d47da7",
                "trade_no": "2015042321001004720200028594",
                "sign": "ERITJKEIJKJHKKKKKKKHJEREEEEEEEEEEE"
            }
        reverse_result = requests.post(request_url, data=pay_result)
        pay_logger.info(reverse_result.content)
    elif pay_way == "wechat":
        pass
    else:
        pass
    order_service.send_order_to_washer_channel(owner_id, group_name, message=order)
