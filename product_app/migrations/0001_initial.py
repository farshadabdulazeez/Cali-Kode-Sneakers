# Generated by Django 4.2.5 on 2023-09-30 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('category_image', models.ImageField(upload_to='category_images/')),
                ('category_description', models.TextField(null=True)),
                ('is_active', models.BooleanField(blank=True, default=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['category_name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=250)),
                ('product_description', models.TextField(blank=True)),
                ('product_image', models.ImageField(blank=True, upload_to='product_images/')),
                ('original_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('selling_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('is_available', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['product_name'],
            },
        ),
        migrations.CreateModel(
            name='ProductBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=150, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('brand_image', models.ImageField(upload_to='brand_images/')),
                ('brand_description', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'ProductBrand',
                'verbose_name_plural': 'ProductBrands',
                'ordering': ['brand_name'],
            },
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.PositiveIntegerField(default=7, unique=True)),
            ],
            options={
                'ordering': ['size'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('product_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.product')),
                ('product_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.productsize')),
            ],
            options={
                'ordering': ['product_size'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product_app.productbrand'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product_app.category'),
        ),
        migrations.CreateModel(
            name='MultipleImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(blank=True, upload_to='multiple_images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_app.product')),
            ],
        ),
    ]
