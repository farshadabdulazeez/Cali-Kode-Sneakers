# Generated by Django 4.2.5 on 2023-11-02 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0010_alter_customuser_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='referral_code',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
