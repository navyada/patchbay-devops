# Generated by Django 3.2.22 on 2023-10-27 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_orders_lender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='orders',
            name='subtotal_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
