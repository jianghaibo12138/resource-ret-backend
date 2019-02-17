from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class Version(APIView):

    def get(self, request):
        return Response("Version 1.0.0", status=status.HTTP_200_OK)
