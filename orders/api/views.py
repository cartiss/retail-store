from webbrowser import get

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.core.validators import URLValidator
from django.http import JsonResponse

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from yaml import load, Loader

from api.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, Basket, UserProfile, \
    ConfirmedBasket
from api.serializers import ProductListSerializer, OrderSerializer, ProductInfoSerializer, BasketSerializer, \
    PartnerSerializer, UserSerializer, OrderPartnerSerializer, PartnerStateSerializer, ConfirmedBasketSerializer
from api.signals import new_user_registered
from orders import settings


class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'password', 'email', 'username'}.issubset(request.data):
            try:
                password = request.data.get('password')
                validate_password(password)
            except Exception as password_er:
                return Response({'Status': False, 'Errors': password_er})
            else:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    user.set_password(request.data.get('password'))
                    new_user_registered.send(sender=self.__class__, user_id=user.id)
                    return JsonResponse({'Status': True, 'Message': 'Confirm your email'})
                return JsonResponse({'Status': False, 'Errors': serializer.errors})
        return JsonResponse({'Status': False, 'Error': 'All required arguments not provided'})


class ConfirmView(APIView):
    pass


class ProductListView(ViewSet):
    def list(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Product.objects.get(id=pk)
        serializer = ProductListSerializer(queryset)

        return Response(serializer.data)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = Order.objects.create(user=request.user,
                                         product=serializer.validated_data.get('product'),
                                         quantity=serializer.validated_data.get('quantity'),
                                         basket=request.user.userprofile.basket,)

            return Response({'Status': True})
        return JsonResponse({'Status': False, 'Errors': serializer.errors})

    def put(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = Order.objects.get(user=request.user.userprofile,
                                      id=serializer.validated_data.get('id'))

            order.update({'quantity': serializer.validated_data.get('quantity'), 'product': serializer.validated_data.get('product')})
            return Response({'Status': True})
        return JsonResponse({'Status': False, 'Errors': serializer.errors})

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(id=request.data.get('id'))
        if order.user == request.user.userprofile:
            order.delete()
            return Response({'Status': True})
        return JsonResponse({'Status': False, 'Errors': 'Can delete only yourself order'})


class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        basket = Basket.objects.get(user=request.user.userprofile)
        serializer = BasketSerializer(basket)
        return JsonResponse(serializer.data)


class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if {'address', 'city', 'mail', 'phone', 'index'}.issubset(request.data):
            if request.user.userprofile.basket.orders.count() == 0:
                return JsonResponse({'Status': False, 'Error': 'There are no orders'})

            serializer = ConfirmedBasketSerializer(data=request.data)

            if serializer.is_valid():
                confirmed_basket = ConfirmedBasket.objects.create(address=serializer.validated_data.get('address'),
                                                                  city=serializer.validated_data.get('city'),
                                                                  index=serializer.validated_data.get('index'),
                                                                  mail=serializer.validated_data.get('mail'),
                                                                  phone=serializer.validated_data.get('phone'),
                                                                  user=request.user)
                orders = Order.objects.filter(basket=request.user.userprofile.basket)
                for order in orders:
                    order.confirmed_basket = confirmed_basket
                    order.basket = None
                    order.save()

                return JsonResponse({'Status': True, 'Message': 'Thank you for your order'})
            return JsonResponse({'Status': False, 'Errors': serializer.errors})
        return JsonResponse({'Status': False, 'Error': 'All required arguments not provided'})


class ConfirmedOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = ConfirmedBasket.objects.filter(user=request.user)
        serializer = ConfirmedBasketSerializer(queryset, many=True)
        return Response(serializer.data)


class PartnerView(ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = Order.objects.filter(product__shop__user=self.request.user.userprofile)
        serializer = OrderPartnerSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Order.objects.get(id=pk)
        serializer = OrderPartnerSerializer(queryset)
        return Response(serializer.data)


class PartnerStateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = UserProfile.objects.get(user=request.user)
        return JsonResponse({'state': queryset.state})

    def post(self, request, *args, **kwargs):
        serializer = PartnerStateSerializer(data=request.data)

        if serializer.is_valid():
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.state = serializer.validated_data.get('state')
            userprofile.save()

            return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Errors': serializer.errors})


class ImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):

        file = request.data.get('file')

        if file:
            data = load(file, Loader=Loader)

            shop, _ = Shop.objects.get_or_create(name=data['shop'], user=self.request.user.userprofile)

            for category in data['categories']:
                category_obj, _ = Category.objects.get_or_create(name=category['name'], id=category['id'])

            for product in data['goods']:
                product_obj, _ = Product.objects.get_or_create(name=product['name'],
                                                            category=Category.objects.get(id=product['category']))
                product_info_obj, _ = ProductInfo.objects.get_or_create(product=product_obj,
                                                                     shop=shop,
                                                                     quantity=product['quantity'],
                                                                     id=product['id'],
                                                                     model=product['model'],
                                                                     price=product['price'],
                                                                     price_rrc=product['price_rrc'])

                for parameter, value in product['parameters'].items():
                    parameter_obj, _ = Parameter.objects.get_or_create(name=parameter)
                    product_parameter_obj, _ = ProductParameter.objects.get_or_create(product_info=product_info_obj,
                                                                                   parameter=parameter_obj,
                                                                                   value=value)

            return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Error': 'No file'})