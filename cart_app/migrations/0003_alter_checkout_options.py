# Generated by Django 4.2.5 on 2023-10-09 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0002_checkout'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='checkout',
            options={'ordering': ['user']},
        ),
    ]
