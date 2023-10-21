from django.db import models
from user_app.models import *
from product_app.models import *
from cart_app.models import *


# Create your models here.


class Payments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    total_amount = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Payments'

    def __str__(self):
        return str(self.payment_id)


class Order(models.Model):
    STATUS = {
        ('ORDER CONFIRMED', 'ORDER CONFIRMED'),
        # ('Shipped', 'Shipped'),
        # ('Out for delivery', 'Out for delivery'),
        # ('Delivered', 'Delivered'),
        # ('Cancelled', 'Cancelled'),
        # ('Return requested', 'Return requested'),
        # ('Return processing', 'Return processing'),
        # ('Returned', 'Returned'),
    }
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=200, null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)
    order_note = models.CharField(max_length=150, null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    order_total = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    # discount = models.FloatField(default=0, blank=True)
    # wallet_amount = models.FloatField(default=0, blank=True, null=True)
    # tax = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS, default="ORDER CONFIRMED")
    # ip = models.CharField(null=True, blank=True)
    is_ordered = models.BooleanField(default=False, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.order_id


class OrderProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    product_price = models.FloatField(null=True, blank=True)
    ordered = models.BooleanField(default=False, null=True, blank=True)
    # return_request = models.BooleanField(default=False)
    # return_accept = models.BooleanField(default=False)
    # is_returned = models.BooleanField(default=False)
    # return_reason = models.TextField(blank=True)
    # item_cancel = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.email} - {self.variant.product.product_name}"