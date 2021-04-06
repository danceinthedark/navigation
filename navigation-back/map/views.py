import random

import numpy as np
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .find_path import *
from .models import Road, Point


# Create your views here.


@csrf_exempt
@require_POST
def map(request):
    try:
        roads = []
        for road in Road.objects.all():
            son = []
            road_info = {}
            for point in road.points.all():
                son.append(point.x)
                son.append(point.y)
            road_info['pos'] = son
            road_info['rid'] = road.id
            road_info['jam_rate'] = road.rate
            roads.append(road_info)

        points = []
        for point in Point.objects.all():
            points.append({'pid': point.id, 'pos': (point.x, point.y), 'name': point.name, 'url': point.img})
        return JsonResponse({"result": "success", "roads": roads, "points": points})
    except:
        return JsonResponse({"result": "fail"})


@csrf_exempt
@require_POST
def search_dest(request):
    try:
        dest = request.POST['dest']
        possible_points = Point.objects.filter(name__contains=dest)
        points = []
        for point in possible_points:
            points.append({'pid': point.id, 'pos': (point.x, point.y), 'url': point.img, 'name': point.name})
            for door in point.doors.all():
                points.append({'pid': door.id, 'pos': (door.x, door.y), 'url': door.img})
        return JsonResponse({"result": "success", "points": points})
    except:
        return JsonResponse({"result": "fail"})


@csrf_exempt
@require_POST
def location(request):
    move((timezone.now() - people.last_ask).seconds)
    people.last_ask = timezone.now()
    return JsonResponse({"result": "success", "x": float(people.pos[0]), "y": float(people.pos[1])}, safe=False)


@csrf_exempt
@require_POST
def search_path(request):
    pid = request.POST['pid']
    approach = [int(i) for i in request.POST['approach'].split(',')]
    dest = Point.objects.get(id=pid)
    result = {}
    result['dist_walk'] = find_path_dist(people.pos[0], people.pos[1], dest, speeds['walk'])
    result['dist_walk']['move_model'] = 'walk'
    result['time_walk'] = find_path_time(people.pos[0], people.pos[1], dest, speeds['walk'])
    result['time_walk']['move_model'] = 'walk'
    result['time_bike'] = find_path_time(people.pos[0], people.pos[1], dest, speeds['bike'])
    result['time_bike']['move_model'] = 'bike'
    result['approach_dist_walk'] = find_approach_dist(people.pos[0], people.pos[1], dest, approach, speeds['walk'])
    result['approach_dist_walk']['move_model'] = 'walk'
    # todO approach_model
    return JsonResponse({"result": "success", "solution": result})


@csrf_exempt
@require_POST
def navigation(request):
    path = request.POST['path'].split(',')
    path = [Point.objects.get(id=i) for i in path]
    people.move_model = request.POST['move_model']
    dis = eucid_distance(people.pos[0], people.pos[1], path[0])
    if dis:
        people.direction = np.array([path[0].x - people.pos[0], path[0].y - people.pos[1]]) / dis
    else:
        people.direction = np.array([0,0])
    people.finish = False

    for road in path[0].edges.all():
        if is_on(people.pos[0], people.pos[1], road):
            people.road_type = road.type
            people.road_jam = road.rate
            break
    people.corner_time = dis / (speeds[people.move_model][people.road_type] * people.road_jam)
    people.path = path
    people.path.reverse()
    people.last_ask = timezone.now()
    people.log.append(
        timezone.now().__format__('%Y-%m-%d %H:%M:%S') + " from {} to {}{}".format(tuple(people.pos), path[-1].name,
                                                                                  (path[-1].x, path[-1].y)))
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def finish(request):
    return JsonResponse({"result": people.finish})


@csrf_exempt
@require_POST
def log(request):
    return JsonResponse({"result": "success", "log": people.log})


def random_road():
    for item in Road.objects.all():
        item.rate = random.random() / 2 + 0.5
        item.save()


def move(t):
    if people.finish:
        return None
    while people.corner_time <= t:
        point_from = people.path.pop()
        if len(people.path):
            road = Road.objects.filter(points=point_from).filter(points=people.path[-1])[0]
            people.road_type = road.type
            people.direction = np.array(
                [people.path[-1].x - point_from.x, people.path[-1].y - point_from.y]) / road.long
            t -= people.corner_time
            people.corner_time = road.long / (speeds[people.move_model][road.type] * road.rate)
            people.road_jam = road.rate
            people.pos = np.array((point_from.x, point_from.y))
        else:
            t = 0
            people.pos = np.array([point_from.x, point_from.y])
            people.finish = True
            break
    people.pos += people.direction * t * speeds[people.move_model][people.road_type] * people.road_jam
    people.corner_time -= t


def import_data():
    pid = open('x_y_id.txt', encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        point = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        item = Point.objects.create(x=float(point[0]), y=float(point[1]))
        if len(point) == 4:
            item.name = point[3]
            item.save()
    pid.close()

    pid = open('x1_y1_x2_y2_dist_line1_line2.txt', encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        road_info = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        road = Road.objects.create(long=float(road_info[4]), type=int(road_info[7]))
        road.save()
        point1 = Point.objects.get(id=road_info[5])
        point2 = Point.objects.get(id=road_info[6])
        point1.edges.add(road)
        point2.edges.add(road)
    random_road()
    pid.close()

    pid = open('line_num_LineNumOfDot.txt', encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        info = [int(i) for i in line.rstrip('\n').split(' ')]
        pid = info.pop(0)
        m = info.pop(0)
        architecture = Point.objects.get(id=pid)
        if m:
            for door_id in info:
                door = Point.objects.get(id=door_id)
                door.belong = architecture
                door.save()
        else:
            architecture.belong = architecture
            architecture.save()
    pid.close()


class Move_point:
    def __init__(self, x, y):
        self.direction = np.array((0, 0))
        self.pos = np.array((x, y))
        self.path = []
        self.road_type = 0
        self.move_model = 'walk'
        self.corner_time = 1e9
        self.log = []
        self.finish = False
        self.last_ask = timezone.now()
        self.road_jam = 1


people = Move_point(63.88703487503486, 703.4870764730676)
walk_speed = [10, 10]
bike_speed = [10, 24]
speeds = {'walk': walk_speed, 'bike': bike_speed}
floyd()
# import_data()
# random_road()
