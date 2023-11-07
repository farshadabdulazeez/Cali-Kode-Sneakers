# Generated by Django 4.2.5 on 2023-11-05 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0032_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('RETURNED', 'RETURNED'), ('CANCELLED', 'CANCELLED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('DELIVERED', 'DELIVERED'), ('SHIPPED', 'SHIPPED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]