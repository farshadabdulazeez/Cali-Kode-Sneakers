# Generated by Django 4.2.5 on 2023-11-03 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0024_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('DELIVERED', 'DELIVERED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('CANCELLED', 'CANCELLED'), ('RETURNED', 'RETURNED'), ('SHIPPED', 'SHIPPED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]
