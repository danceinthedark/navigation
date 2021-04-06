# Generated by Django 3.0.6 on 2021-03-29 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_road_direction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='road',
            name='direction',
        ),
        migrations.AddField(
            model_name='road',
            name='vec_x',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='road',
            name='vec_y',
            field=models.FloatField(default=0),
        ),
    ]
