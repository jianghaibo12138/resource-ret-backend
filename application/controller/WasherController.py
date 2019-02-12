from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.models import Washer
from application.serializers import WasherSerializer


class WasherRegisteView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = WasherSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response('Information of washer is not completion.', status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WasherDetailView(APIView):
    def get(self, request, id):
        try:
            washer = Washer.objects.get(id=id)
        except Exception as e:
            return Response('Washer not found, {}'.format(id), status=status.HTTP_404_NOT_FOUND)
        serializer = WasherSerializer(washer, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        try:
            washer = Washer.objects.get(id=id)
        except Exception as e:
            return Response('Washer not found, {}'.format(id), status=status.HTTP_404_NOT_FOUND)
        serializer = WasherSerializer(washer, data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response('Update washer info failed.', status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


