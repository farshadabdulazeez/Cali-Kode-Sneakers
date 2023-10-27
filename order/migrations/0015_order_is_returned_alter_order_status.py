# Generated by Django 4.2.5 on 2023-10-26 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_order_item_cancelled_order_item_returned_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_returned',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('DELIVERED', 'DELIVERED'), ('RETURN PROCESSING', 'RETURN PROCESSING'), ('SHIPPED', 'SHIPPED'), ('RETURN REQUESTED', 'RETURN REQUESTED'), ('RETURNED', 'RETURNED'), ('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('CANCELLED', 'CANCELLED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]
