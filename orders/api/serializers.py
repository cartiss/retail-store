from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.response import Response

from api.models import Order, Product, OrderProduct, Shop, ProductInfo


class ShopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = []


class ProductListSerializer(serializers.ModelSerializer):
    shops = ShopsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'category', 'shops')


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ('model', 'quantity', 'price', 'price_rrc')


class OrderSerializer(serializers.ModelSerializer):
    products = ProductInfoSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('user', 'status', 'products', 'dt')


    def create(self, validated_data):
        order = Order.objects.create(status=True, user=User.objects.get(id=1)) # user=self.context['request'].user
        order_product = OrderProduct.objects.create(order=order, product=validated_data['product'], quantity=validated_data['quantity'])
        return Response({'Status': 'ok'})