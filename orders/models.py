from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

STATUS_CHOICES = [(0, "pending"), (1, "success"), (2, "error")]


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField(validators=[MinValueValidator(0.0)])


class Order(models.Model):
    price = models.FloatField(validators=[MinValueValidator(limit_value=0.0)])
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(
        Product, through="OrderProduct", related_name="orders"
    )


class OrderProduct(models.Model):
    units = models.IntegerField(validators=[MinValueValidator(1)])
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )


class OrderMarketplace(models.Model):
    marketplace_name = models.CharField(max_length=50)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="marketplaces"
    )
    date_create = models.DateTimeField(auto_now_add=True, null=True)
    date_success = models.DateTimeField(null=True)
    date_error = models.DateTimeField(null=True)
    url_marketplace = models.URLField(null=True)
    api_method = models.CharField(max_length=10, null=True)
    api_call_error_msg = models.TextField(blank=True)


class OrderAmazonFake(OrderMarketplace):
    def save(self, *args, **kwargs):
        self.marketplace_name = "AmazonFake"
        self.url_marketplace = "https://fakestoreapi.com/carts"
        self.api_method = "post"
        super().save(*args, **kwargs)


class OrderAliexpressFake(OrderMarketplace):
    def save(self, *args, **kwargs):
        self.marketplace_name = "AliexpressFake"
        self.url_marketplace = "https://fake-store-api.mock.beeceptor.com/api/orders"
        self.api_method = "put"
        super().save(*args, **kwargs)
