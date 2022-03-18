# Generated by Django 2.0.5 on 2018-10-18 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0049_colour_hex_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='vic_price',
            field=models.DecimalField(decimal_places=4, default=0.0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='zincalume_discount_victoria',
            field=models.DecimalField(decimal_places=4, default=0.0, max_digits=20),
        ),
    ]