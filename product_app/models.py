from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from user_app.models import *


class Category(models.Model):
    category_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category_image = models.ImageField(upload_to='category_images/')
    category_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, null=False, blank=True)

    class Meta:
        ordering = ['category_name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.category_name)


class ProductBrand(models.Model):
    brand_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    brand_image = models.ImageField(upload_to='brand_images/')
    brand_description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['brand_name']
        verbose_name = 'ProductBrand'
        verbose_name_plural = 'ProductBrands'

    def __str__(self):
        return '{}'.format(self.brand_name)


class ProductSize(models.Model):
    size = models.PositiveIntegerField(default=7, unique=True)
    size_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['size']

    def __str__(self):
        return str(self.size_name)


class Product(models.Model):
    product_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=250, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, null=True)
    product_description = models.TextField(blank=True)
    product_image = models.ImageField(upload_to='product_images/', blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['product_name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])

    def __str__(self):
        return '{}'.format(self.product_name)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['product_size']

    def __str__(self):
        return f"{self.product.product_name} - size : {self.product_size.size}"


class MultipleImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='multiple_images/', blank=True)

    class Meta:
        verbose_name_plural = 'Multiple Images'

    def __str__(self):
        return self.product.product_name
    

