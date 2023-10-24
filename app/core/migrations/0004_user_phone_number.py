# Generated by Django 3.2.22 on 2023-10-24 06:12

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default='0000000000', max_length=128, region=None, unique=True),
            preserve_default=False,
        ),
    ]