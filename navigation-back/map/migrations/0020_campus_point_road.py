# Generated by Django 3.0.6 on 2021-04-22 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('map', '0019_auto_20210422_1004'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campus', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.FloatField(default=1)),
                ('long', models.FloatField()),
                ('type', models.IntegerField(default=0)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roads', to='map.Campus')),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('img', models.URLField(blank=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('belong', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doors', to='map.Point')),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='map.Campus')),
                ('edges', models.ManyToManyField(related_name='points', to='map.Road')),
            ],
        ),
    ]
