from datetime import datetime, timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.utils import timezone
from rest_framework.authtoken.models import Token

ROLE_WASHER = "ROLE_WASHER"


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuthUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tel_phone = models.CharField(max_length=11, blank=False, null=False, default="")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    # class Meta:
    #     ordering = ("-createAt", )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        old_user = AuthUser.objects.filter(pk=self.id).first()
        if old_user:
            if old_user.password != self.password:
                Token.objects.filter(user=self).update(user=self)
        super(AuthUser, self).save(*args, **kwargs)


class Order(BaseModel):
    WAITING_PAY = "WAITING_PAY"
    ORDER_PAYED = "ORDER_PAYED"
    WAITING_WASHING = "WAITING_WASHING"
    ORDER_TIMEOUT = "ORDER_TIMEOUT"
    ORDER_FINISH = "ORDER_FINISH"
    ORDER_CANCEL = "ORDER_CANCEL"
    ORDER_REFUND = "ORDER_REFUND"
    ORDER_STATUS = [
        ("waiting_pay", WAITING_PAY),
        ("order_payed", ORDER_PAYED),
        ("waiting_washing", WAITING_WASHING),
        ("order_timeout", ORDER_TIMEOUT),
        ("order_finish", ORDER_FINISH),
        ("order_cancel", ORDER_CANCEL),
        ("order_refund", ORDER_REFUND)
    ]
    washer = models.ForeignKey("Washer", on_delete=models.CASCADE, blank=True, null=True)
    longitude = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    status = models.CharField(choices=ORDER_STATUS, max_length=20, default=WAITING_PAY)
    owner = models.ForeignKey('AuthUser', on_delete=models.CASCADE)

    # class Meta:
    #     ordering = ("-createAt", )


class Washer(BaseModel):
    name = models.CharField(max_length=50)
    master_phone = models.CharField(max_length=11, blank=False, null=False, default='')
    longitude = models.CharField(default="", max_length=10)
    latitude = models.CharField(default="", max_length=10)
    logo = models.ImageField(default="")

    # class Meta:
    #     ordering = ("-createAt", )


class CancelOrder(BaseModel):
    REGRET_ORDER = "不想下单了"
    WRONG_SERVICE_ITEM = "选错服务项目"
    TIMEOUT = "付款超时"
    REASON_TYPE = [
        ("regret to continue the order", REGRET_ORDER),
        ("wrong service item", WRONG_SERVICE_ITEM),
        ("order timeout", TIMEOUT),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    owner = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    reason = models.TextField(max_length=800, blank=True, null=True)
    reason_type = models.CharField(choices=REASON_TYPE, max_length=20, blank=False, null=False)

    class Meta:
        ordering = ("-createAt",)


class VerifyCode(BaseModel):
    verify_code = models.CharField(max_length=6, blank=False, null=False)
    tel_phone = models.CharField(max_length=20, blank=False, null=False)
    expire_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.expire_time = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-createAt",)


class OrderPayedLog(BaseModel):
    api_name = models.CharField(max_length=100, blank=False, null=False)
    code = models.CharField(max_length=10, blank=False, null=False)
    message = models.CharField(max_length=30, blank=False, null=False)
    out_trade_no = models.ForeignKey(Order, on_delete=models.CASCADE)
    trade_no = models.CharField(max_length=50, blank=False, null=False)
    sign = models.CharField(max_length=500, null=False, blank=False)

    class Meta:
        ordering = ("-createAt",)


class WebsocketChannel(BaseModel):
    GROUP_NAME_CHOICES = [
        ("group_name_choices", settings.CHANNEL_GROUP_TEMPLATE)
    ]
    channel_name = models.CharField(max_length=100, blank=False, null=False)
    owner = models.ForeignKey(AuthUser, null=True, blank=True, on_delete=models.CASCADE)
    washer = models.ForeignKey(Washer, null=True, blank=True, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=20, choices=GROUP_NAME_CHOICES, default="")
    is_group = models.BooleanField(default=False)

    class Meta:
        ordering = ("-createAt",)
