from django.db import models
from user_app.models import *
from product_app.models import *
from django.core.validators import MinValueValidator, MaxValueValidator



class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)  
    date_added = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    single_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['created_date']

    def sub_total(self):

        return self.product.product.selling_price * self.quantity 

    def __str__(self):
        return f"{self.product.product.product_name} - size : {self.product.product_size.size}"
    

from django.db import models
from django.core.validators import MinValueValidator

class Coupons(models.Model):
    coupon_code = models.CharField(max_length=25, blank=True, null=True)
    discount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    minimum_order_amount = models.IntegerField(
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)
    description = models.TextField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.coupon_code


