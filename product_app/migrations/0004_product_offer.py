# Generated by Django 4.2.5 on 2023-11-05 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_app', '0003_productbrand_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]