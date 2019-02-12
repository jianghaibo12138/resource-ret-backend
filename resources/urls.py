"""resources URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

import application.controller.UserController as UserController
import application.controller.OrderController as OrderController
from application.controller import WasherController

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(title='Resources API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

app_name = 'resource'

admin_patterns = [
    # admin site
    path('admin/', admin.site.urls),
]

user_patterns = [
    # user api
    path('user-registe/', UserController.CustomRegisteView.as_view(), name='user-registe'),
    path('user-login/', UserController.CustomLoginView.as_view(), name='user-login'),
    path('user-all/', UserController.AllCustomsView.as_view(), name='user-all'),
    path('user-detail/<str:id>', UserController.CustomDetailView.as_view(), name='user-detail'),
    path('send-verify-code/', UserController.VerifyCodeView.as_view(), name='send-verify-code'),
]

order_patterns = [
    # order api
    path('order-all/', OrderController.AllOrdersView.as_view(), name='order-all'),
    path('order-record/', OrderController.OrderRecordView.as_view(), name='order-record'),
    path('order-detail/<str:id>', OrderController.OrderDetailView.as_view(), name='order-detail'),
    path('order-pay/<str:id>', OrderController.OrderPayView.as_view(), name='order-pay'),
    path('order-payed/', OrderController.PayedOrdersView.as_view(), name='order-payed'),

    path('cancel-order/<str:id>', OrderController.CancelOrderView.as_view(), name='cancel-order'),
    path('cancel-order-all', OrderController.AllCancelOrdersView.as_view(), name='cancel-order-all'),
    path('cancel-order-detail/<str:id>', OrderController.CancelOrderDetailView.as_view(), name='cancel-order-detail'),
]

washer_patterns = [
    path('washer-registe/', WasherController.WasherRegisteView.as_view(), name='washer-all'),
    path('washer-detail/<str:id>', WasherController.WasherDetailView.as_view(), name='washer-detail'),
]

urlpatterns = [
    url('docs/', schema_view, name="docs"),
    url('admin/', admin.site.urls),
    url('api/v1/user/', include((user_patterns, app_name), namespace="user")),
    url('api/v1/order/', include((order_patterns, app_name), namespace="order")),
    url('api/v1/washer/', include((washer_patterns, app_name), namespace="washer")),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
