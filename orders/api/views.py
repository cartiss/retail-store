from webbrowser import get

from django.core.validators import URLValidator
from django.http import JsonResponse

# Create your views here.
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from yaml import load, Loader

from api.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order
from api.serializers import ProductListSerializer


class ProductListView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


class ImportView(APIView):

    def post(self, request, *args, **kwargs):

        file = request.data.get('file')

        if file:
            data = load(file, Loader=Loader)
            shop, _ = Shop.objects.get_or_create(name=data['shop'])

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
        return JsonResponse({'Status': False, 'Error': 'no file'})