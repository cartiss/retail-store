from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Shop(models.Model):

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'

    name = models.CharField(verbose_name='Shop name', max_length=50, unique=True)
    url = models.URLField(verbose_name='Shop url')
    filename = models.CharField(verbose_name='Filename', max_length=50)


class Category(models.Model):

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    shops = models.ManyToManyField('Shop',
                                   related_name='categories',
                                   blank=True)
    name = models.CharField(max_length=50, unique=True)


class Product(models.Model):

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    shops = models.ManyToManyField('Shop', related_name='products', through='ProductInfo')


class ProductInfo(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    model = models.CharField(null=True, max_length=128)
    price = models.PositiveIntegerField()
    price_rrc = models.PositiveIntegerField()


class Parameter(models.Model):

    class Meta:
        verbose_name = 'Parameter'
        verbose_name_plural = 'Parameters'

    name = models.CharField(max_length=150)
    products = models.ManyToManyField('ProductInfo', related_name='parameters', through='ProductParameter')


class ProductParameter(models.Model):
    product_info = models.ForeignKey('ProductInfo', on_delete=models.CASCADE)
    parameter = models.ForeignKey('Parameter', on_delete=models.CASCADE)
    value = models.CharField(max_length=100)


class Order(models.Model):

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dt = models.DateField(auto_now_add=True)
    status = models.BooleanField()
    products = models.ManyToManyField('Product', related_name='orders', through='OrderProduct')


class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE) # product_info foreignkey
    quantity = models.PositiveIntegerField()


class Contact(models.Model):

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    TYPES_CHOICES = [
        ('email', 'E-mail'),
        ('phone', 'Phone number')
    ]
    type = models.CharField(
        max_length=50,
        choices=TYPES_CHOICES
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, unique=True)


