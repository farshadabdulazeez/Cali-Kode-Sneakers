# Generated by Django 4.2.5 on 2023-10-20 17:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_orderproduct_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='product',
        ),
    ]
