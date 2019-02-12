from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from application.models import AuthUser, Order, Washer, CancelOrder, VerifyCode, OrderPayedLog


class AuthUserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(read_only=True)
    tel_phone = serializers.CharField(max_length=11)
    username = serializers.CharField(write_only=True, min_length=6, required=False)
    first_name = serializers.CharField(min_length=2, required=False)
    last_name = serializers.CharField(min_length=2, required=False)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(min_length=6, required=False)
    url = serializers.HyperlinkedIdentityField(view_name="user:user-detail", lookup_field="id")

    def create(self, validated_data):
        validated_data['username'] = validated_data.get('tel_phone')
        user = super(AuthUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    @staticmethod
    def validate_password(value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(detail=e.messages)
        return value

    class Meta:
        model = AuthUser
        fields = '__all__'


class WasherSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(read_only=True)
    master_phone = serializers.CharField(min_length=11)
    name = serializers.CharField(min_length=2)
    longitude = serializers.CharField(write_only=True)
    latitude = serializers.CharField(write_only=True)
    location = serializers.SerializerMethodField()
    logo = serializers.CharField(required=False)
    url = serializers.HyperlinkedIdentityField(view_name="washer:washer-detail", lookup_field="id")

    @staticmethod
    def get_location(object):
        return {
            "lat": object.latitude,
            "lon": object.longitude
        }

    def update(self, instance, validate_data):
        instance.master_phone = validate_data.get('master_phone', instance.master_phone)
        instance.name = validate_data.get('name', instance.name)
        instance.logo = validate_data.get('logo', instance.logo)
        return instance

    class Meta:
        model = Washer
        fields = "__all__"


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.UUIDField(read_only=True)
    washer = serializers.UUIDField(write_only=True, required=False)
    washer_json = WasherSerializer(many=True, read_only=True)
    longitude = serializers.FloatField(write_only=True)
    latitude = serializers.FloatField(write_only=True)
    location = serializers.SerializerMethodField("get_locations", read_only=True)
    desc = serializers.SerializerMethodField(read_only=True)
    price = serializers.FloatField(required=True)
    discount = serializers.FloatField(required=True)
    owner_json = AuthUserSerializer(many=True, read_only=True)
    owner = serializers.UUIDField(write_only=True)
    status = serializers.CharField(min_length=2, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="order:order-detail", lookup_field="id")

    @staticmethod
    def get_locations(object):
        return {
            "lat": object.latitude,
            "lon": object.longitude
        }

    @staticmethod
    def get_desc(object):
        return object.washer.name

    def create(self, validated_data):
        validated_data['washer'] = Washer.objects.filter(id=validated_data['washer']).first()
        validated_data['owner'] = AuthUser.objects.filter(id=validated_data['owner']).first()
        return Order.objects.create(**validated_data)

    class Meta:
        model = Order
        fields = "__all__"


class CancelOrderSerializer(serializers.HyperlinkedModelSerializer):
    order = OrderSerializer(read_only=True)
    owner = AuthUserSerializer(read_only=True)
    owner_id = serializers.UUIDField(write_only=True)
    order_id = serializers.UUIDField(write_only=True)
    reason = serializers.CharField(min_length=8, allow_blank=True)
    reason_type = serializers.CharField(min_length=2)
    url = serializers.HyperlinkedIdentityField(view_name="order:cancel-order-detail", lookup_field="id")

    def create(self, validated_data):
        cancel_order = super(CancelOrderSerializer, self).create(validated_data)
        return cancel_order

    class Meta:
        model = CancelOrder
        fields = "__all__"


class VerifyCodeSerializer(serializers.ModelSerializer):
    tel_phone = serializers.CharField(required=True)
    verify_code = serializers.CharField(required=True)

    class Meta:
        model = VerifyCode
        fields = "__all__"


class OrderPayedLogSerializer(serializers.ModelSerializer):
    api_name = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
    out_trade_no = serializers.CharField(write_only=True, required=True)
    order_info = serializers.SerializerMethodField(read_only=True)
    trade_no = serializers.CharField(required=True)
    sign = serializers.CharField(required=True)

    class Meta:
        model = OrderPayedLog
        fields = "__all__"

    @staticmethod
    def get_order_info(object):
        return object.id if object else ""

    def create(self, validated_data):
        order = Order.objects.filter(id=validated_data.get('out_trade_no')).first()
        if not order:
            raise ResourceWarning
        validated_data['out_trade_no'] = order
        order_log = super(OrderPayedLogSerializer, self).create(validated_data)
        return order_log
