# Generated by Django 3.2.22 on 2023-10-26 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_listingreviews_listingreview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listingreview',
            name='text',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
