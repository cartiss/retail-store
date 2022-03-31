from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from api.views import ImportView, ProductListView, OrderView, BasketView, PartnerView, RegistrationView, \
    PartnerStateView, ConfirmOrderView, ConfirmedOrdersView, ConfirmEmailView

router = routers.SimpleRouter()
router.register(r'products', ProductListView, basename='products')
router.register(r'partner/order', PartnerView, basename='partner_order')

urlpatterns = [
    path('api/v1/update/', ImportView.as_view(), name='import'),
    path('api/v1/', include(router.urls)),
    path('api/v1/login/', obtain_auth_token),
    path('api/v1/basket/', BasketView.as_view(), name='basket'),
    path('api/v1/basket/confirm/', ConfirmOrderView.as_view(), name='basket_confirm'),
    path('api/v1/confirmed/', ConfirmedOrdersView.as_view(), name='confirmed_orders'),
    path('api/v1/orders/', OrderView.as_view(), name='orders'),
    path('api/v1/partner/state/', PartnerStateView.as_view(), name='partner_order'),
    path('api/v1/registration/', RegistrationView.as_view(), name='registration'),
    path('api/v1/registration/confirm/', ConfirmEmailView.as_view(), name='registration_confirm'),
]

