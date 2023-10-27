# Generated by Django 4.2.5 on 2023-10-25 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancel_reason',
            field=models.CharField(blank=True, choices=[('NO LONGER NEEDED', 'NO LONGER NEEDED'), ('FOUND A BETTER DEAL', 'FOUND A BETTER DEAL'), ('ORDERED BY MISTAKE', 'ORDERED BY MISTAKE'), ('CHANGED MY MIND', 'CHANGED MY MIND')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='return_reason',
            field=models.CharField(blank=True, choices=[('DEFECTIVE PRODUCT', 'DEFECTIVE PRODUCT'), ('RECEIVED WRONG ITEM', 'RECEIVED WRONG ITEM'), ('ITEM DAMAGED DURING SHIPPING', 'ITEM DAMAGED DURING SHIPPING'), ('CHANGED MY MIND', 'CHANGED MY MIND')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('OUT OF DELIVERY', 'OUT OF DELIVERY'), ('RETURN PROCESSING', 'RETURN PROCESSING'), ('RETURN REQUESTED', 'RETURN REQUESTED'), ('SHIPPED', 'SHIPPED'), ('DELIVERED', 'DELIVERED'), ('RETURNED', 'RETURNED'), ('ORDER CONFIRMED', 'ORDER CONFIRMED'), ('CANCELLED', 'CANCELLED')], default='ORDER CONFIRMED', max_length=50),
        ),
    ]
