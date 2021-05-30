import os

import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .find_path import *
from .models import Road, Point


# Create your views here.


@csrf_exempt
@require_POST
def give_map(request):
    random_road()
    global f
    try:
        root = Point.objects.get(id=request.POST['id'])
        node, links = obtain_road(root)
        return JsonResponse({"result": "success", "links": links, "node": node})
    except:
        return JsonResponse({"result": "fail"})




def choose_bus(start, end, time):
    time = (time + (timezone.now() - start_time).seconds) / 60
    time -= time // 60 * 60
    school_bus = 0
    for launch in schoolbus_table:
        if launch >= time:
            school_bus = launch - time + 1
            break
    bus = 1 - (time - int(time)) + bus_cost
    dest = 1 if start == Point.objects.get(id=2) else 0
    if school_bus > bus:
        return [{'type': 2, 'path': [(start.x, start.y, start.z), (end.x, end.y, end.z)], 'dist': 0, 'time': bus * 3600,
                 'move_model': 'bus', 'id': dest}]
    else:
        return [{'type': 2, 'path': [(start.x, start.y, start.z), (end.x, end.y, end.z)], 'dist': 0, 'time': bus * 3600,
                 'move_model': 'bus', 'id': dest}]


@csrf_exempt
@require_POST
def search_path(request):
    dest = request.POST['dest']
    try:
        dest = Point.objects.get(name__contains=dest)
        x = float(request.POST['x'])
        y = float(request.POST['y'])
        z = float(request.POST['z'])
        pid = int(request.POST['id'])
        model = int(request.POST['model'])
        approach = []
        if model == 3:
            approach = [Point.objects.get(name__contains=s) for s in request.POST['approach'].split(',')]

        result = []
        root1 = pid if pid < 3 else Point.objects.get(id=pid).belong.id
        root2 = dest.belong.id if dest.belong.id < 3 else Point.objects.get(id=dest.belong.id).belong.id
        approach1 = []
        approach2 = []
        for point in approach:
            root = point.belong.id if point.belong.id < 3 else Point.objects.get(id=point.belong.id).belong.id
            if root == root1:
                approach1.append(point.id)
            elif root == root2:
                approach2.append(point.id)
        last = timezone.now()
        if root1 == root2:
            if model == 0:
                result = find_path_dist(pid, x, y, z, dest, speeds['walk'], 'walk')[0]
                cost_time = (timezone.now() - last).microseconds
            elif model == 1:
                result = find_path_time(pid, x, y, z, dest, speeds['walk'], 'walk')[0]
                cost_time = (timezone.now() - last).microseconds
            elif model == 2:
                result = find_path_time(pid, x, y, z, dest, speeds['bike'], 'bike')[0]
                cost_time = (timezone.now() - last).microseconds
            else:
                result = find_approach_dist(pid, x, y, z, dest, approach1, speeds['walk'], 'walk')[0]
                cost_time = (timezone.now() - last).microseconds
        else:
            door1 = Point.objects.get(id=root1).inner_points.get(name__contains="校门")
            door2 = Point.objects.get(id=root2).inner_points.get(name__contains="校门")
            if model == 0:
                [result, time] = find_path_dist(pid, x, y, z, door1, speeds['walk'], 'walk')
                result += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
                result += find_path_dist(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['walk'], 'walk')[0]
                cost_time = (timezone.now() - last).microseconds
            elif model == 1:
                [result, time] = find_path_time(pid, x, y, z, door1, speeds['walk'], 'walk')
                result += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
                result += find_path_time(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['walk'], 'walk')[0]
                cost_time = (timezone.now() - last).microseconds
            elif model == 2:
                [result, time] = find_path_time(pid, x, y, z, door1, speeds['bike'], 'bike')
                result += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
                result += find_path_time(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['bike'], 'bike')[0]
                cost_time = (timezone.now() - last).microseconds
            else:
                [result, time] = find_approach_dist(pid, x, y, z, door1, approach1, speeds['walk'], 'walk')
                result += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
                result += \
                    find_approach_dist(door2.belong.id, door2.x, door2.y, door2.z, dest, approach1, speeds['walk'],
                                       'walk')[0]
                cost_time = (timezone.now() - last).microseconds

        return JsonResponse({"result": "success", "cost_time": cost_time, "solution": result})
    except:
        return JsonResponse({"result": "fail"})


@csrf_exempt
@require_POST
def writeLog(request):
    with open("navigation.log", 'a', encoding='utf-8')as f:
        express = timezone.now().__format__('%Y-%m-%d %H:%M:%S') + ' ' + request.POST['log'] + '\n'
        f.writelines(express)
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def finish(request):
    store()
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def log(request):
    with open("navigation.log", encoding='utf-8') as fd:
        lines = fd.readlines()
        return JsonResponse({"result": "success", "log": lines})


@csrf_exempt
@require_POST
def around(request):
    x = float(request.POST['x'])
    y = float(request.POST['y'])
    z = 0
    root = request.POST['id']
    root = Point.objects.get(id=root)
    points = list(people.root.inner_points.filter(name__regex='^[\S\s]+'))

    nearer_points = find_nearer_point(root, x, y, z)
    overall = eucid_distance(x, y, z, nearer_points[0])
    d = [item + overall for item in dijkstra(nearer_points[0])]
    if len(nearer_points) > 1:
        overall = eucid_distance(x, y, z, nearer_points[1])
        g = dijkstra(nearer_points[1])
        d = [min(d[i], g[i] + overall) for i in range(len(d))]
    points.sort(key=lambda item: d[item.id])
    near_points = points[:5]
    points = []
    for point in near_points:
        points.append({'id': point.id, 'dist': d[point.id]})
    return JsonResponse({'result': "success", "points": points})




# def move(t):
#     if people.finish:
#         return None
#     while people.corner_time <= t:
#         last_pos = people.path[-1]['path'].pop()
#         point_from = Point.objects.get(x=last_pos[0], y=last_pos[1], z=last_pos[2])
#         if len(people.path[-1]['path']):
#             next_pos = people.path[-1]['path'][-1]
#             point_to = Point.objects.get(x=next_pos[0], y=next_pos[1], z=next_pos[2])
#             if point_from.belong == point_to.belong:
#                 road = point_from.edge.filter(points=point_to)[0]
#                 people.road_type = road.type
#                 people.direction = np.array(
#                     [point_to.x - point_from.x, point_to.y - point_from.y, point_to.z - point_from.z]) / road.long
#                 t -= people.corner_time
#                 #TODO 改到这，不确定需不需要move
#                 people.corner_time = road.long / (speeds[people.move_model][road.type] * road.rate)
#                 people.road_jam = road.rate
#                 people.pos = np.array((point_from.x, point_from.y, point_from.z))
#             else:
#                 people.corner_time = people.path[-1]['time']
#                 people.direction = np.array(0, 0, 0)
#         else:
#             people
#             t -= people.corner_time
#             people.pos = np.array([point_from.x, point_from.y])
#             people.path.pop()
#             people.direction = np.array([0, 0])
#         if len(people.path) == 0:
#             people.finish = 1
#             t = 0
#     people.pos += people.direction * t * speeds[people.move_model][people.road_type] * people.road_jam
#     people.corner_time -= t


def import_data(file):
    import os
    pid = open(os.path.join(file, 'x_y_id.txt'), encoding='utf-8')
    lines = pid.readlines()
    campus = Point.objects.get(name=file)
    for line in lines:
        point = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        item = Point.objects.create(x=float(point[0]), y=float(point[1]), belong=campus)
        if len(point) > 3:
            item.name = point[3]
            item.save()
    pid.close()

    pid = open(os.path.join(file, 'x1_y1_x2_y2_dist_line1_line2.txt'), encoding='utf-8')
    lines = pid.readlines()
    for line in lines:
        road_info = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        road = Road.objects.create(long=float(road_info[4]), type=int(road_info[7]), belong=campus,
                                   rate=random.random())
        point1 = Point.objects.get(id=road_info[5])
        point2 = Point.objects.get(id=road_info[6])
        road.points.add(point1)
        road.points.add(point2)
    pid.close()

def import_architecture(id):
    pid = open(os.path.join('architecture', "dot_f{}.txt".format(id)), encoding="utf-8")
    lines = pid.readlines()
    for line in lines:
        info = line.replace('\'', '').replace(' ', '').replace('[', '').replace(']', '').rstrip('\n').split(',')
        point = Point.objects.create(x=info[1], y=info[2], z=info[3], belong_id=info[0])
        flag = int(info[5])
        if flag == 1:
            door = Point.objects.get(id=int(info[6]))
            road = Road.objects.create(long=1e-5, belong_id=info[0])
            road.points.add(point)
            road.points.add(door)
        elif flag == 3:
            point.name = info[6] + "_" + info[7] + "_" + info[8]
            point.save()

    pid.close()
    pid = open(os.path.join('architecture', "draw_f{}.txt".format(id)), encoding="utf-8")
    lines = pid.readlines()
    for line in lines:
        info = line.replace('\'', '').replace(' ', '').replace('[', '').replace(']', '').rstrip('\n').split(',')
        architecture = Point.objects.get(id=int(info[0]))
        start = architecture.inner_points.all()[0].id
        point1 = architecture.inner_points.get(id=int(info[1]) + start - 1)
        point2 = architecture.inner_points.get(id=int(info[2]) + start - 1)
        info[3] = float(info[3])
        if info[3] == 0:
            info[3] = 1e-5
        road = Road.objects.create(long=info[3], belong_id=info[0])

        road.points.add(point1)
        road.points.add(point2)
    pid.close()


class Move_point:
    def __init__(self, x, y, z):
        self.direction = np.array((0, 0))
        self.pos = np.array((x, y, z))
        self.root = Point.objects.get(id=1)
        self.path = []
        self.road_type = 0
        self.move_model = 'walk'
        self.corner_time = 1e9
        self.log = []
        self.last_ask = timezone.now()
        self.road_jam = 1


def import_picture():
    files = os.listdir(settings.IMAGE_DIR)
    for file_name in files:
        ids = file_name.replace('.svg', '').split('_')
        for pid in ids:
            item = Point.objects.get(id=pid)
            item.img = 'http://127.0.0.1:8000/image/{}'.format(file_name)
            item.save()


if Point.objects.count() == 0:
    Point.objects.create(name="沙河")
    Point.objects.create(name="西土城")
    import_data("沙河")
    import_data("西土城")
    for i in range(1, 8):
        import_architecture(i)
    import_picture()
init()
people = Move_point(0, 130, 0)
walk_speed = [5, 5]
bike_speed = [5, 12]
speeds = {'walk': walk_speed, 'bike': bike_speed}
last_update_road = timezone.now()
now = 1
schoolbus_table = [2, 4, 7, 9, 10, 12]  # one day is 14minutes，denote 14 hours
schoolbus_cost = 1
bus_cost = 2
start_time = timezone.now()
