# Generated by Django 3.0.6 on 2021-05-15 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0027_auto_20210512_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='road',
            name='points',
            field=models.ManyToManyField(related_name='edges', to='map.Point'),
        ),
    ]
