# Generated by Django 3.0.6 on 2021-05-28 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('map', '0033_auto_20210528_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField(default=0)),
                ('y', models.FloatField(default=0)),
                ('z', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=20)),
                ('img', models.URLField(blank=True)),
                ('belong', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inner_points', to='map.Point')),
            ],
        ),
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField(default=1)),
                ('long', models.FloatField()),
                ('type', models.IntegerField(default=0)),
                ('belong', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inner_roads', to='map.Point')),
                ('points', models.ManyToManyField(related_name='edges', to='map.Point')),
            ],
        ),
    ]
