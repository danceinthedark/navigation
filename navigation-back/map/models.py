from django.db import models


class Campus(models.Model):
    campus = models.CharField(max_length=20)


class Road(models.Model):
    rate = models.FloatField(default=1)
    long = models.FloatField()
    type = models.IntegerField(default=0)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='roads')


class Point(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    edges = models.ManyToManyField(Road, related_name='points')
    img = models.URLField(blank=True)
    name = models.CharField(blank=True, max_length=100)
    belong = models.ForeignKey('self', on_delete=models.CASCADE, related_name='doors', blank=True, null=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='points')
