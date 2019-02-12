from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.mixins import BasicAuthMixin
from application.models import Order, CancelOrder, WebsocketChannel
from application.serializers import OrderSerializer, CancelOrderSerializer, OrderPayedLogSerializer
from resources.celery_app import pay_for_order


class AllOrdersView(APIView):

    def get(self, request):
        """
        获取所有订单
        response_serializer: OrderSerializer
        parameters:
            - name: body
              pytype: CigarSerializerMinimal
              paramType: body
        """
        order_queryset = Order.objects.filter().all()
        order_serializer = OrderSerializer(order_queryset, many=True, context={'request': request})
        return Response(order_serializer.data)


class OrderRecordView(APIView):

    def post(self, request):
        """用户新建订单"""
        order_serilizer = OrderSerializer(data=request.data, context={'request': request})
        if not order_serilizer.is_valid():
            return Response(order_serilizer.errors, status=status.HTTP_400_BAD_REQUEST)
        order_serilizer.save()
        return Response(order_serilizer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """洗车店接受订单"""
        order = Order.objects.filter(id=request.data.get("order_id")).first()
        if not order:
            return Response("Order not found.", status=status.HTTP_404_NOT_FOUND)
        order.status = order.WAITING_WASHING
        order.save()
        order_serializer = OrderSerializer(order, context={"request": request})
        return Response(data=order_serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):

    def get(self, request, id):
        """获取订单详情"""
        try:
            order_questset = Order.objects.get(id=id)
        except Exception as e:
            order_questset = []
        if not order_questset:
            return Response("Order not found for id: {}".format(id), status=status.HTTP_400_BAD_REQUEST)
        order_serializer = OrderSerializer(order_questset, context={'request': request})
        return Response(order_serializer.data)


class OrderPayView(BasicAuthMixin, APIView):

    def post(self, request, id):
        """支付订单"""
        # order = Order.objects.filter(id=id, owner=request.user).first()
        order = Order.objects.filter(id=id).first()
        if not order:
            return Response(data="Order information not found ID: {}".format(id), status=status.HTTP_404_NOT_FOUND)
        order.status = order.WAITING_WASHING
        order.save()
        order_serializer = OrderSerializer(order, context={'request': request})
        channel_obj = WebsocketChannel.objects.filter(owner=request.user, is_group=True,
                                                      group_name=settings.CHANNEL_GROUP_TEMPLATE).first()
        if channel_obj:
            pay_for_order.delay(group_name=settings.CHANNEL_GROUP_TEMPLATE, order=order_serializer.data,
                                pay_way=request.data.get('pay_way'), owner_id=request.user.id)

        return Response('success')


class PayedOrdersView(APIView):

    def get(self, request):
        """获取所有支付过的订单"""
        order_queryset = Order.objects.filter(status=Order.ORDER_PAYED).all()
        order_serialiser = OrderSerializer(order_queryset, many=True, context={'request': request})
        return Response(order_serialiser.data)

    def post(self, request):
        """支付完成写入数据库"""
        order_id = request.data.get('out_trade_no')
        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response("Order not exists.", status=status.HTTP_404_NOT_FOUND)
        order.status = order.ORDER_PAYED
        order.save()
        serializer = OrderPayedLogSerializer(data=request.data)
        if not serializer.is_valid():
            return Response("Order payed log info is not valid.", status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllCancelOrdersView(APIView):

    def get(self, request):
        """所有取消的订单"""
        cancel_order_queryset = CancelOrder.objects.filter().all()
        cancel_order_serializer = CancelOrderSerializer(cancel_order_queryset, many=True, context={'request': request})
        return Response(cancel_order_serializer.data)


class CancelOrderView(BasicAuthMixin, APIView):

    def post(self, request, id):
        """取消订单"""
        order = Order.objects.filter(id=id).first()
        if not order:
            return Response(data="Order information not found ID: {}".format(id), status=status.HTTP_404_NOT_FOUND)
        request.data['order_id'] = id
        request.data['owner_id'] = request.user.id
        cancel_order_serializer = CancelOrderSerializer(data=request.data, context={'request': request})
        if not cancel_order_serializer.is_valid():
            return Response(data="Cancel order's information not correct.", status=status.HTTP_400_BAD_REQUEST)

        order.status = order.ORDER_CANCEL
        order.save()
        cancel_order_serializer.save()
        return Response(cancel_order_serializer.data)


class CancelOrderDetailView(APIView):

    def get(self, request, id):
        """已经取消的订单的详情"""
        cancel_order_queryset = CancelOrder.objects.filter(id=id).first()
        if not cancel_order_queryset:
            return Response(data="Cancel order information not found, ID: {}".format(id))
        cancel_order_serializer = CancelOrderSerializer(cancel_order_queryset, context={'request': request})
        return Response(data=cancel_order_serializer.data)
