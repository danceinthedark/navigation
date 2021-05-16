# Generated by Django 3.0.6 on 2021-05-12 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0024_campus_point_road'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='point',
            name='belong',
        ),
        migrations.RemoveField(
            model_name='point',
            name='campus',
        ),
        migrations.RemoveField(
            model_name='point',
            name='edges',
        ),
        migrations.RemoveField(
            model_name='road',
            name='campus',
        ),
        migrations.DeleteModel(
            name='Campus',
        ),
        migrations.DeleteModel(
            name='Point',
        ),
        migrations.DeleteModel(
            name='Road',
        ),
    ]