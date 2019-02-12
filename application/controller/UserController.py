import random

from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from application.mixins import SuperUserMixin
from application.models import AuthUser, VerifyCode
from application.serializers import AuthUserSerializer, VerifyCodeSerializer
from resources.celery_app import send_verify_code
from resources.settings import API_CALL_TIME_LIMIT, API_CALL_FREQUENCY_LIMIT
from resources.wrappers import request_frequency_single_ip


class CustomLoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        request.data['username'] = request.data.get('tel_phone')
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": "Token {}".format(token.key)})


class CustomRegisteView(APIView):

    def post(self, request):
        if AuthUser.objects.filter(username=request.data.get('tel_phone')).exists():
            return Response('Phone number already registed. Try to login directly',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response("Telephone number and verify code are required.", status=status.HTTP_400_BAD_REQUEST)
        instance = VerifyCode.objects.filter(
            tel_phone=serializer.data.get('tel_phone'), verify_code=serializer.data.get('verify_code'),
            expire_time__gte=timezone.now())
        if not instance.exists():
            return Response("Verify code is expired.", status=status.HTTP_406_NOT_ACCEPTABLE)
        instance.delete()

        user_serializer = AuthUserSerializer(data=request.data, context={'request': request})
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_serializer.save()
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class AllCustomsView(SuperUserMixin, APIView):

    def get(self, request):
        user_queryset = AuthUser.objects.all()
        user_serializer = AuthUserSerializer(user_queryset, many=True, context={'request': request})
        return Response(user_serializer.data)


class CustomDetailView(APIView):
    def get(self, request, id):
        try:
            user_questset = AuthUser.objects.get(id=id)
        except Exception as e:
            user_questset = []
        if not user_questset:
            return Response("User not found for id: {}".format(id), status=status.HTTP_400_BAD_REQUEST)
        user_serializer = AuthUserSerializer(user_questset, context={'request': request})
        return Response(user_serializer.data)


class VerifyCodeView(APIView):

    @request_frequency_single_ip(API_CALL_TIME_LIMIT.get('call_every_60s'), API_CALL_FREQUENCY_LIMIT.get('frequency_1'))
    def post(self, request):
        tel_phone = request.data.get('tel_phone')
        if not tel_phone:
            return Response("Please post a telephone number.", status=status.HTTP_400_BAD_REQUEST)
        verify_code = []
        for _ in range(6):
            verify_code.append(str(random.randint(0, 9)))
        verify_code = "".join(verify_code)
        VerifyCode.objects.update_or_create(tel_phone=tel_phone, defaults={'verify_code': verify_code})
        send_verify_code.delay(tel_phone, verify_code)
        return Response("success", status=status.HTTP_200_OK)
