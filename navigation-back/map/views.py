import random
import re

import numpy as np
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .find_path import *
from .models import Road, Point, Campus


# Create your views here.


@csrf_exempt
@require_POST
def give_map(request):
    try:
        campus = Campus.objects.get(campus=request.POST['campus'])
        roads = []
        for road in campus.roads.all():
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
        for point in campus.points.all():
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
            points.append({'pid': point.id, 'pos': (point.x, point.y),
                           'url': point.img, 'name': point.name, 'in_campus': point.campus == people.campus})
            for door in point.doors.all():
                points.append({'pid': door.id, 'pos': (door.x, door.y), 'url': door.img,
                               'in_campus': point.campus == people.campus})
        return JsonResponse({"result": "success", "points": points})
    except:
        return JsonResponse({"result": "fail"})


@csrf_exempt
@require_POST
def location(request):
    move((timezone.now() - people.last_ask).seconds)
    people.last_ask = timezone.now()
    return JsonResponse({"result": "success", "x": float(people.pos[0]), "y": float(people.pos[1]) ,'finish':people.finish}, safe=False)


def choose_bus(f, t, time):
    time = (time + (timezone.now() - start_time).seconds) / 60
    time -= time // 60 * 60
    school_bus = 0
    for launch in schoolbus_table:
        if launch >= time:
            school_bus = launch - time + 1
            break
    bus = 1 - (time - int(time)) + bus_cost
    if school_bus > bus:
        return {'path': [f, t], 'time': bus * 3600, 'way': 'bus'}
    else:
        return {'path': [f, t], 'time': school_bus * 3600, 'way': 'school_bus'}


@csrf_exempt
@require_POST
def search_path_campus(request):
    global last_update_road
    random_road((timezone.now() - last_update_road).seconds)
    last_update_road = timezone.now()
    pid = request.POST['pid']
    approach = [int(i) for i in request.POST['approach'].split(',')]
    approach1 = []
    approach2 = []
    for point in approach:
        if Point.objects.get(id=point).campus == people.campus:
            approach1.append(point)
        else:
            approach2.append(point)

    dest = Point.objects.get(id=pid)
    door = people.campus.points.get(name='校门')
    new_door = dest.campus.points.get(name='校门')
    result = {}
    # first to gateway and choose bus
    result['dist_walk'] = {}
    result['dist_walk']['path'] = [
        find_path_dist(people.campus, people.pos[0], people.pos[1], door, speeds['walk'])]
    result['dist_walk']['path'].append(choose_bus(door.id, new_door.id, result['dist_walk']['path'][0]['time']))
    result['dist_walk']['move_model'] = 'walk'

    result['time_walk'] = {}
    result['time_walk']['path'] = [
        find_path_time(people.campus, people.pos[0], people.pos[1], door, speeds['walk'])]
    result['time_walk']['path'].append(choose_bus(door.id, new_door.id, result['time_walk']['path'][0]['time']))
    result['time_walk']['move_model'] = 'walk'

    result['time_bike'] = {}
    result['time_bike']['path'] = [
        find_path_time(people.campus, people.pos[0], people.pos[1], door, speeds['bike'])]
    result['time_bike']['path'].append(choose_bus(door.id, new_door.id, result['time_bike']['path'][0]['time']))
    result['time_bike']['move_model'] = 'bike'

    result['approach_dist_walk'] = {}
    result['approach_dist_walk']['path'] = [
        find_approach_dist(people.campus, people.pos[0], people.pos[1], door, approach1, speeds['walk'])]
    result['approach_dist_walk']['path'].append(
        choose_bus(door.id, new_door.id, result['approach_dist_walk']['path'][0]['time']))
    result['approach_dist_walk']['move_model'] = 'walk'

    # from door to dest

    result['dist_walk']['path'].append(
        find_path_dist(dest.campus, new_door.x, new_door.y, dest, speeds['walk']))
    result['time_walk']['path'].append(
        find_path_time(dest.campus, new_door.x, new_door.y, dest, speeds['walk']))
    result['time_bike']['path'].append(
        find_path_time(dest.campus, new_door.x, new_door.y, dest, speeds['bike']))
    result['approach_dist_walk']['path'].append(
        find_approach_dist(dest.campus, new_door.x, new_door.y, dest, approach2, speeds['walk']))
    return JsonResponse({"result": "success", "solution": result})


@csrf_exempt
@require_POST
def search_path(request):
    global last_update_road
    random_road((timezone.now() - last_update_road).seconds)
    last_update_road = timezone.now()
    pid = request.POST['pid']
    approach = [int(i) for i in request.POST['approach'].split(',')]
    dest = Point.objects.get(id=pid)
    result = dict()
    result['dist_walk'] = find_path_dist(people.campus, people.pos[0], people.pos[1], dest, speeds['walk'])
    result['dist_walk']['move_model'] = 'walk'
    result['time_walk'] = find_path_time(people.campus, people.pos[0], people.pos[1], dest, speeds['walk'])
    result['time_walk']['move_model'] = 'walk'
    result['time_bike'] = find_path_time(people.campus, people.pos[0], people.pos[1], dest, speeds['bike'])
    result['time_bike']['move_model'] = 'bike'
    result['approach_dist_walk'] = find_approach_dist(people.campus, people.pos[0], people.pos[1], dest, approach,
                                                      speeds['walk'])
    result['approach_dist_walk']['move_model'] = 'walk'
    return JsonResponse({"result": "success", "solution": result})


@csrf_exempt
@require_POST
def navigation(request):
    path = str(request.POST['path']).replace(' ', '')
    count = path.count('path')
    paths = []
    if count > 0:
        last = 0
        for i in range(3):
            pos = path.find('path', last)
            start = path.find('[', pos)
            end = path.find(']', pos)
            new_path = path[start + 1:end].split(',')
            new_path = [Point.objects.get(id=i) for i in new_path]
            if i == 1:
                time_start = path.find('time', end) + 4
                people.bus_time = float(re.search("\d*", path[time_start + 2:]).group(0))
            paths.append(new_path)
            last = end
    else:
        path = path.split(',')
        paths.append([Point.objects.get(id=i) for i in path])
    people.move_model = request.POST['move_model']
    dis = eucid_distance(people.pos[0], people.pos[1], paths[0][0])
    if dis:
        people.direction = np.array([paths[0][0].x - people.pos[0], paths[0][0].y - people.pos[1]]) / dis
    else:
        people.direction = np.array([0, 0])
    people.finish = False

    for road in paths[0][0].edges.all():
        if is_on(people.pos[0], people.pos[1], road):
            people.road_type = road.type
            people.road_jam = road.rate
            break
    people.corner_time = dis / (speeds[people.move_model][people.road_type] * people.road_jam)
    people.path = paths
    people.path.reverse()
    for i in range(len(people.path)):
        people.path[i].reverse()
    people.last_ask = timezone.now()
    people.log.append(
        timezone.now().__format__('%Y-%m-%d %H:%M:%S') +
        " from {} in campus {} to {}{} in campus {}".format(tuple(people.pos), people.campus, paths[-1][-1].name,
                                                            (paths[-1][-1].x, paths[-1][-1].y), paths[-1][-1].campus))
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def finish(request):
    if len(people.path) > 0:
        people.pos = np.array([people.path[-1][0].x, people.path[-1][0].y])
        people.path.pop()
        people.corner_time = 0
        if len(people.path) == 0:
            people.finish = 1
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def log(request):
    return JsonResponse({"result": "success", "log": people.log})


@csrf_exempt
@require_POST
def around(request):
    points = list(people.campus.points.filter(name__regex='^[\S\s]+'))
    points.sort(key=lambda item: eucid_distance(people.pos[0], people.pos[1], item))
    near_points = points[:5]
    points = []
    for point in near_points:
        points.append({'pid': point.id, 'pos': (point.x, point.y), 'name': point.name, 'url': point.img})
    return JsonResponse({'result': "success", "points": points})


def random_road(t):
    t = min(t, 10)
    n = Road.objects.count()
    if t == 0:
        t = n
    global now
    for i in range(now, min(n + 1, now + t)):
        item = Road.objects.get(id=i)
        item.rate = random.random()
        item.save()
    now += t
    if now > Road.objects.count():
        now = 1


def move(t):
    if people.finish:
        return None
    while people.corner_time <= t:
        point_from = people.path[-1].pop()

        if len(people.path[-1]):
            if point_from.campus == people.path[-1][-1].campus:
                road = point_from.campus.roads.filter(points=point_from).filter(points=people.path[-1][-1])[0]
                people.road_type = road.type
                people.direction = np.array(
                    [people.path[-1][-1].x - point_from.x, people.path[-1][-1].y - point_from.y]) / road.long
                t -= people.corner_time
                people.corner_time = road.long / (speeds[people.move_model][road.type] * road.rate)
                people.road_jam = road.rate
                people.pos = np.array((point_from.x, point_from.y))
            else:
                people.corner_time = people.bus_time
        else:
            t -= people.corner_time
            people.pos = np.array([point_from.x, point_from.y])
            people.path.pop()
            people.direction = np.array([0, 0])
            if len(people.path) == 0:
                people.finish = 1
                t = 0
    people.pos += people.direction * t * speeds[people.move_model][people.road_type] * people.road_jam
    people.corner_time -= t


def import_data(file):
    import os
    if len(Campus.objects.filter(campus=file)) == 0:
        campus = Campus.objects.create(campus=file)
    else:
        return
    pid = open(os.path.join(file, 'x_y_id.txt'), encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        point = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        item = Point.objects.create(x=float(point[0]), y=float(point[1]), campus=campus)
        if len(point) == 4:
            item.name = point[3]
            item.save()
    pid.close()

    pid = open(os.path.join(file, 'x1_y1_x2_y2_dist_line1_line2.txt'), encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        road_info = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        road = Road.objects.create(long=float(road_info[4]), type=int(road_info[7]), campus=campus,
                                   rate=random.random())
        point1 = Point.objects.get(id=road_info[5])
        point2 = Point.objects.get(id=road_info[6])
        point1.edges.add(road)
        point2.edges.add(road)
    pid.close()

    pid = open(os.path.join(file, 'line_num_LineNumOfDot.txt'), encoding='utf-8')
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
        self.campus = Campus.objects.get(campus='沙河')
        self.bus_time = 0


# import_data("沙河")
# import_data("西土城")
floyd(0, Campus.objects.get(id=1))
floyd(Campus.objects.get(id=1).points.count(), Campus.objects.get(id=2))
people = Move_point(0, 130)
walk_speed = [5, 5]
bike_speed = [5, 12]
speeds = {'walk': walk_speed, 'bike': bike_speed}
last_update_road = timezone.now()
now = 1
schoolbus_table = [2, 4, 7, 9, 10, 12]  # one day is 14minutes，denote 14 hours
schoolbus_cost = 1
bus_cost = 2
start_time = timezone.now()
