# Generated by Django 3.2.22 on 2023-10-30 02:39

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.user_image_file_path),
        ),
    ]
