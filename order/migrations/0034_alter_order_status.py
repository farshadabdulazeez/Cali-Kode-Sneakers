# Generated by Django 4.2.5 on 2023-11-06 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0033_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('RETURNED', 'RETURNED'), ('DELIVERED', 'DELIVERED'), ('SHIPPED', 'SHIPPED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('CANCELLED', 'CANCELLED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]
