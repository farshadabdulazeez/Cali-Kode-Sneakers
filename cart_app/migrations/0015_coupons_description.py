# Generated by Django 4.2.5 on 2023-11-01 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0014_remove_coupons_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupons',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
