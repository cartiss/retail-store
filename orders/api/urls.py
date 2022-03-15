from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from api.views import ImportView, ProductListView, OrderView

router = routers.DefaultRouter()
router.register(r'products', ProductListView, basename='products_router')
router.register(r'orders', OrderView, basename='orders')

urlpatterns = [
    path('api/v1/update/', ImportView.as_view(), name='import_view'),
    path('api/v1/', include(router.urls), name='api_view'),
]

