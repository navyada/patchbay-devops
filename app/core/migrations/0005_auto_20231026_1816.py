# Generated by Django 3.2.22 on 2023-10-26 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20231026_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='saved',
            name='listing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.listing'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='saved',
            unique_together={('user', 'listing')},
        ),
        migrations.RemoveField(
            model_name='saved',
            name='listing',
        ),
    ]