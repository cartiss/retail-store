from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Order, Product, Shop, ProductInfo, Basket, UserProfile, ConfirmedBasket, Contact


class ShopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'products')


class ProductListSerializer(serializers.ModelSerializer):
    shops = ShopsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'shops')


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ('model', 'quantity', 'price', 'price_rrc')


class OrderSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'product', 'dt', 'quantity')

    def to_representation(self, instance):
        self.fields['product'] = ProductInfoSerializer(read_only=True)
        return super(OrderSerializer, self).to_representation(instance)


class OrderPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'status', 'product', 'dt')

    def to_representation(self, instance):
        self.fields['product'] = ProductInfoSerializer(read_only=True)
        return super(OrderPartnerSerializer, self).to_representation(instance)


class PartnerStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('state',)


class BasketSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ('orders',)


class ConfirmedBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmedBasket
        fields = ('address', 'phone', 'city', 'mail', 'index')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}


class PartnerSerializer(serializers.ModelSerializer):
    product = ProductInfoSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'product', 'status', 'dt', 'quantity', 'user')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('phone', 'index', 'address', 'city')

