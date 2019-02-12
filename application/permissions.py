from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import BasePermission

CURRENT_AUTH_SETTING = (TokenAuthentication, SessionAuthentication)


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
