import asyncio
from webbrowser import get

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import URLValidator
from django.http import JsonResponse

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from yaml import load, Loader

from api.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, Basket, UserProfile, \
    ConfirmedBasket
from api.serializers import ProductListSerializer, OrderSerializer, ProductInfoSerializer, BasketSerializer, \
    PartnerSerializer, UserSerializer, OrderPartnerSerializer, PartnerStateSerializer, ConfirmedBasketSerializer, \
    ContactSerializer
from orders import settings


class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        '''
        Registration view, required fields: first_name, last_name, password, email, username
        with confirm email
        '''
        if {'first_name', 'last_name', 'password', 'email', 'username'}.issubset(request.data):
            try:
                password = request.data.get('password')
                validate_password(password)
            except Exception as password_er:
                return Response({'Status': False, 'Errors': password_er}, status=HTTP_400_BAD_REQUEST)
            else:
                serializer = UserSerializer(data=request.data)
                if serializer.is_valid():
                    is_user_registered = User.objects.filter(email=serializer.validated_data.get('email')).first()
                    if not is_user_registered:
                        user, _ = User.objects.get_or_create(email=serializer.validated_data.get('email'),
                                                             username=serializer.validated_data.get('username'),
                                                             first_name=serializer.validated_data.get('first_name'),
                                                             last_name=serializer.validated_data.get('last_name'),)
                        user.is_active = False
                        user.is_staff = False
                        user.set_password(request.data.get('password'))
                        user.save()
                        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)

                        async def send_email():
                            '''
                            Message to user email
                            '''
                            msg = EmailMultiAlternatives(
                                f"Password Reset Token for {token.user.email}",
                                token.key,
                                settings.EMAIL_HOST_USER,
                                [token.user.email]
                            )
                            msg.send()

                        async def async_send_email():
                            '''
                            Acync tasks
                            '''
                            tasks = []
                            task = asyncio.create_task(send_email())
                            tasks.append(task)
                            await asyncio.gather(*tasks)

                        asyncio.run(async_send_email())

                        return JsonResponse({'Status': True, 'Message': 'Confirm your email'})
                    return JsonResponse({'Status': False, 'Errors': 'Email have already registered'}, status=HTTP_400_BAD_REQUEST)
                return JsonResponse({'Status': False, 'Errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)
        return JsonResponse({'Status': False, 'Error': 'All required arguments not provided'}, status=HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    def post(self, request, *args, **kwargs):
        '''
        Post request to confirm email
        Required fields: token, email
        '''
        if {'token', 'email'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data.get('email'),
                                                     key=request.data.get('token')).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()

                return JsonResponse({'Status': True}, status=200)
            return JsonResponse({'Status': False, 'Errors': 'Incorrect email or token'}, status=HTTP_400_BAD_REQUEST)
        return JsonResponse({'Status': False, 'Errors': 'All required arguments not provided'}, status=HTTP_400_BAD_REQUEST)


class ProductListView(ViewSet):
    def list(self, request, *args, **kwargs):
        '''
        List of products with state=True
        '''
        products = Product.objects.filter(shops__user__userprofile__state=True)
        serializer = ProductListSerializer(products, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        '''
        Info about specific product by pk
        '''
        queryset = Product.objects.get(id=pk)
        serializer = ProductListSerializer(queryset)

        return Response(serializer.data)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        '''
        Post request to create order.
        Required fields: product, quantity
        After creation, this order will be in user's basket
        '''
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            order = Order.objects.create(user=request.user,
                                         product=serializer.validated_data.get('product'),
                                         quantity=serializer.validated_data.get('quantity'),
                                         basket=request.user.userprofile.basket,)
            return JsonResponse({'Status': True}, status=HTTP_200_OK)
        return JsonResponse({'Status': False, 'Errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        '''
        Delete order from basket and in general
        '''
        order = Order.objects.get(id=request.data.get('id'))
        if order.user == request.user:
            order.delete()
            return JsonResponse({'Status': True}, status=HTTP_200_OK)
        return JsonResponse({'Status': False, 'Errors': 'Can delete only yourself order'}, status=HTTP_400_BAD_REQUEST)


class BasketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
        Get orders in user's basket
        '''
        basket = Basket.objects.get(user=request.user.userprofile)
        serializer = BasketSerializer(basket)
        return JsonResponse(serializer.data)


class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        '''
        Post request to confirm orders in user's basket
        Required fields: address, city, index, mail, phone
        After confirmation, will be created ConfirmBasket with all user's orders
        '''
        if {'address', 'city', 'mail', 'phone', 'index'}.issubset(request.data):
            if request.user.userprofile.basket.orders.count() == 0:
                return JsonResponse({'Status': False, 'Error': 'There are no orders'}, status=HTTP_400_BAD_REQUEST)

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
            return JsonResponse({'Status': False, 'Errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)
        return JsonResponse({'Status': False, 'Error': 'All required arguments not provided'}, status=HTTP_400_BAD_REQUEST)


class ConfirmedOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = ConfirmedBasket.objects.filter(user=request.user)
        serializer = ConfirmedBasketSerializer(queryset, many=True)
        return Response(serializer.data)


class PartnerView(ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        '''
        List of partner orders
        '''
        queryset = Order.objects.filter(product__shop__user=self.request.user)
        serializer = OrderPartnerSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        '''
        Get specific partner order by id
        '''
        queryset = Order.objects.get(id=pk)
        serializer = OrderPartnerSerializer(queryset)
        return Response(serializer.data)


class PartnerStateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        '''
        Get partner state
        '''
        queryset = UserProfile.objects.get(user=request.user)
        return JsonResponse({'state': queryset.state})

    def post(self, request, *args, **kwargs):
        '''
        Change partner state
        Required field: 'state' with value - on or off
        '''
        if {'state'}.issubset(request.data):
            serializer = PartnerStateSerializer(data=request.data)

            if serializer.is_valid():
                userprofile = UserProfile.objects.get(user=request.user)
                userprofile.state = serializer.validated_data.get('state')
                userprofile.save()
                return JsonResponse({'Status': True})
            return JsonResponse({'Status': False, 'Errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)
        return JsonResponse({'Status': False, 'Errors': 'All required arguments not provided'}, status=HTTP_400_BAD_REQUEST)


class ImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        '''
        Import yaml file with info about shop, categories and products
        '''
        file = request.data.get('file')

        if file:
            data = load(file, Loader=Loader)

            shop, _ = Shop.objects.get_or_create(name=data['shop'], user=self.request.user)

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
        return JsonResponse({'Status': False, 'Error': 'No file'}, status=HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        '''
        Change products info via yaml file
        '''
        file = request.data.get('file')

        if file:
            data = load(file, Loader=Loader)
            shop, _ = Shop.objects.get_or_create(name=data['shop'], user=self.request.user)

            for category in data['categories']:
                category_obj, _ = Category.objects.get_or_create(name=category['name'], id=category['id'])

            for product in data['goods']:
                product_obj, _ = Product.objects.get_or_create(name=product['name'],
                                                               category=product['category'])
                product_info_obj, _ = ProductInfo.objects.get_or_create(product=product_obj,
                                                                        shop=shop,
                                                                        id=product['id'],)
                product_info_obj.update(price=product['price'],
                                        price_rcc=product['price_rrc'],
                                        quantity=product['quantity'])

                for parameter, value in product['parameters'].items():
                    parameter_obj, _ = Parameter.objects.get_or_create(name=parameter)
                    product_parameter_obj, _ = ProductParameter.objects.get_or_create(product_info=product_info_obj,
                                                                                      parameter=parameter_obj,
                                                                                      value=value)

            return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Error': 'No file'}, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        '''
        Delete products from db via yaml file
        '''
        file = request.data.get('file')

        if file:
            data = load(file, Loader=Loader)
            shop, _ = Shop.objects.get(name=data['shop'], user=self.request.user)

            for product in data['goods']:
                product_obj = Product.objects.get(name=product['name'],
                                                  category=product['category'])
                product_info_obj = ProductInfo.objects.get(product=product_obj,
                                                           shop=shop,
                                                           id=product['id'], )

                for parameter, value in product['parameters'].items():
                    parameter_obj, _ = Parameter.objects.get(products__product_info=product_info_obj).delete()
                    product_parameter_obj, _ = ProductParameter.objects.get(product_info=product_info_obj).delete()

                product_info_obj.delete()

            return JsonResponse({'Status': True})
        return JsonResponse({'Status': False, 'Error': 'No file'}, status=HTTP_400_BAD_REQUEST)
