# Generated by Django 4.2.5 on 2023-10-31 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CANCELLED', 'CANCELLED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('DELIVERED', 'DELIVERED'), ('SHIPPED', 'SHIPPED'), ('RETURNED', 'RETURNED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]
