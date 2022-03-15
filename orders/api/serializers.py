from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response

from api.models import Order, Product, OrderProduct


class ProductListSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0)

    class Meta:
        model = Product
        fields = ('shops', 'name', 'quantity')


    def create(self, validated_data):
        order = Order.objects.create(status=True, user=User.objects.get(id=1)) # user=self.context['request'].user
        order_product = OrderProduct.objects.create(order=order, product=validated_data['product'], quantity=validated_data['quantity'])
        return Response({'Status': 'ok'})