from django.db import models


class Point(models.Model):
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.IntegerField(default=0)
    name = models.CharField(max_length=20)
    img = models.URLField(blank=True)
    belong = models.ForeignKey('self', on_delete=models.CASCADE, related_name='inner_points', blank=True, null=True)


class Road(models.Model):
    rate = models.FloatField(default=1)
    long = models.FloatField()
    type = models.IntegerField(default=0)  # 是否为自行车道
    points = models.ManyToManyField(Point, related_name='edges')
    belong = models.ForeignKey(Point, on_delete=models.CASCADE, related_name='inner_roads', null=True)
