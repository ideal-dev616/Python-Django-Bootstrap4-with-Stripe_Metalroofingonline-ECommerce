# Generated by Django 2.0.5 on 2018-07-05 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0045_auto_20180704_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='preload_lengths_short_list',
            field=models.BooleanField(default=False, help_text='Add the shorter list of lengths'),
        ),
    ]