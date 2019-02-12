from application.permissions import CURRENT_AUTH_SETTING, IsAuthenticated, IsAdminUser


class BasicMixin:
    authentication_classes = CURRENT_AUTH_SETTING


class BasicAuthMixin(BasicMixin):
    permission_classes = (IsAuthenticated,)


class SuperUserMixin(BasicMixin):
    permission_classes = (IsAdminUser,)
