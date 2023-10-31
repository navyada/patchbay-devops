# Generated by Django 3.2.22 on 2023-10-30 18:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_rename_userimages_userimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listing',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]
