# Generated by Django 3.0.6 on 2021-03-29 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='road',
            name='direction',
            field=models.CharField(default='(0,1)', max_length=100),
        ),
    ]