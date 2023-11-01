# Generated by Django 4.2.5 on 2023-11-01 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('SHIPPED', 'SHIPPED'), ('CANCELLED', 'CANCELLED'), ('RETURNED', 'RETURNED'), ('DELIVERED', 'DELIVERED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]