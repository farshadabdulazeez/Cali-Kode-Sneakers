# Generated by Django 4.2.5 on 2023-10-30 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('RETURNED', 'RETURNED'), ('CANCELLED', 'CANCELLED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('SHIPPED', 'SHIPPED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('DELIVERED', 'DELIVERED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]