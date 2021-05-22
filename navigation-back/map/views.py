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
    try:
        root = Point.objects.get(id=request.POST['id'])
        roads = []
        for road in root.inner_roads.all():
            son = []
            road_info = {}
            interact = False
            for point in road.points.all():
                if point.belong != root:
                    interact = True
                son.append(point.x)
                son.append(point.y)
            if interact:
                continue
            road_info['pos'] = son
            road_info['rid'] = road.id
            road_info['jam_rate'] = road.rate
            roads.append(road_info)

        points = []
        for point in root.inner_points.all():
            points.append({'pid': point.id, 'pos': (point.x, point.y), 'url': point.img})
        return JsonResponse({"result": "success", "roads": roads, "points": points})
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
    random_road()
    dest = request.POST['dest']
    dest = Point.objects.get(id=dest)
    x = float(request.POST['x'])
    y = float(request.POST['y'])
    z = float(request.POST['z'])
    pid = int(request.POST['id'])
    approach = [int(i) for i in request.POST['approach'].split(',')]

    result = {}
    root1 = pid if pid < 3 else Point.objects.get(id=pid).belong.id
    root2 = dest.belong.id if dest.belong.id < 3 else Point.objects.get(id=dest.belong.id).belong.id
    approach1 = []
    approach2 = []
    for item in approach:
        point = Point.objects.get(id=item)
        root = point.belong.id if point.belong.id < 3 else Point.objects.get(id=point.belong.id).belong.id
        if root == root1:
            approach1.append(item)
        elif root == root2:
            approach2.append(item)
    cost_time = []
    last = timezone.now()
    if root1 == root2:
        result['dist'] = find_path_dist(pid, x, y, z, dest, speeds['walk'], 'walk')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()
        result['time'] = find_path_time(pid, x, y, z, dest, speeds['walk'], 'walk')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()
        result['transportation'] = find_path_time(pid, x, y, z, dest, speeds['bike'], 'bike')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()
        result['approach'] = find_approach_dist(pid, x, y, z, dest, approach1, speeds['bike'], 'bike')[0]
        cost_time.append((timezone.now() - last).microseconds)
    else:
        door1 = Point.objects.get(id=root1).inner_points.get(name__contains="校门")
        door2 = Point.objects.get(id=root2).inner_points.get(name__contains="校门")
        [result['dist'], time] = find_path_dist(pid, x, y, z, door1, speeds['walk'], 'walk')
        result['dist'] += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
        result['dist'] += find_path_dist(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['walk'], 'walk')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()

        [result['time'], time] = find_path_time(pid, x, y, z, door1, speeds['walk'], 'walk')
        result['time'] += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
        result['time'] += find_path_time(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['walk'], 'walk')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()

        [result['transportation'], time] = find_path_time(pid, x, y, z, door1, speeds['bike'], 'bike')
        result['transportation'] += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
        result['transportation'] += find_path_time(door2.belong.id, door2.x, door2.y, door2.z, dest, speeds['bike'],
                                                   'bike')[0]
        cost_time.append((timezone.now() - last).microseconds)
        last = timezone.now()

        [result['approach'], time] = find_approach_dist(pid, x, y, z, door1, approach1, speeds['bike'], 'bike')
        result['approach'] += choose_bus(door1, door2, time + (timezone.now() - start_time).seconds)
        result['approach'] += find_approach_dist(door2.belong.id, door2.x, door2.y, door2.z, dest, approach1,
                                                 speeds['bike'], 'bike')[0]
        cost_time.append((timezone.now() - last).microseconds)

    return JsonResponse({"result": "success", "cost_time": cost_time, "solution": result})


@csrf_exempt
@require_POST
def navigation(request):
    # path = request.POST['path'].replace(' ', '')
    # paths = []
    # start = 0
    # s = ''
    # for char in path:
    #     if char == '{':
    #         start = 1
    #         s = ''
    #     elif char == '}':
    #         start = 0
    #         items = s.split(',')
    #         segment = {}
    #         for item in items:
    #             [key, value] = item.split(':')
    #             key = key.split('\'')
    #             if key in ['type', 'id']:
    #                 value = int(value)
    #             elif key in ['dist', 'time']:
    #                 value = float(value)
    #             elif key != 'move_model':
    #                 ls = []
    #                 value = value[1:-2].replace('(', '').replace(')', '').split(',')
    #                 point = []
    #                 for item in value:
    #                     point.append(item)
    #                     if len(point) == 3:
    #                         ls.append(tuple(point))
    #                         point = []
    #                 ls.reverse()
    #                 value = ls
    #             segment[key] = value
    #         paths.append(segment)
    #     elif start == 1:
    #         s += char
    # paths.reverse()
    # people.path = paths
    # next = people.path[-1]['path'].pop()
    # people.pos = np.array(paths[-1]['path'][-1])
    # people.move_model = paths[-1]['move_model']
    # people.root = Point.objects.get(id=paths[-1]['id'])
    # dis = eucid_distance(people.pos[0], people.pos[1], people.pos[2], next)
    # if dis == 0:
    #     dis = 1
    # people.direction = np.array(next[0] - people.pos[0], next[1] - people.pos[1], next[2] - people.pos[2]) / dis
    # next = Point.objects.get(id=people.root).inner_points.get(x=next[0], y=next[1], z=next[2])
    # for road in next.edge.all():
    #     if is_on(people.pos[0], people.pos[1], people.pos[2], road):
    #         people.road_type = road.type
    #         people.road_jam = road.rate
    #         break
    # people.corner_time = dis / (speeds[people.move_model][people.road_type] * people.road_jam)
    # people.last_ask = timezone.now()
    # dest = Point.objects.get(id=paths[0]['id']).inner_points.get(id=paths[0]['path'][0])
    # people.log.append(
    #     timezone.now().__format__('%Y-%m-%d %H:%M:%S') +
    #     " from {} in {} to {}{} in  {}".format(tuple(people.pos), people.root.name, dest.name,
    #                                            (dest.x, dest.y, dest.z), dest.belong.name))
    people.log.append(request.POST['log'])
    return JsonResponse({"result": "success"})


@csrf_exempt
@require_POST
def finish(request):
    store()
    return JsonResponse({"result": "success"})

@csrf_exempt
@require_POST
def log(request):
    return JsonResponse({"result": "success", "log": people.log})


@csrf_exempt
@require_POST
def around(request):
    points = list(people.root.inner_points.filter(name__regex='^[\S\s]+'))
    points.sort(key=lambda item: eucid_distance(people.pos[0], people.pos[1], people.pos[2], item))
    near_points = points[:5]
    points = []
    for point in near_points:
        points.append({'pid': point.id, 'pos': (point.x, point.y, point.z), 'name': point.name, 'url': point.img})
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
    pid = open(os.path.join(file, 'x_y_id_1.txt'), encoding='utf-8')
    lines = pid.readlines()
    campus = Point.objects.get(name=file)
    for line in lines:
        point = line.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '').rstrip('\n').split(',')
        item = Point.objects.create(x=float(point[0]), y=float(point[1]), belong=campus)
        if len(point) > 3:
            item.name = point[3]
            item.save()
    pid.close()

    pid = open(os.path.join(file, 'x1_y1_x2_y2_dist_line1_line2_1.txt'), encoding='utf-8')
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


def import_architecture(path):
    pid = open(os.path.join('architecture', 'zip', path, "buidingId_x_y_z_id_flag_phy_logi1_logi2.txt"),
               encoding="utf-8")
    lines = pid.readlines()
    i = 0
    for line in lines:
        info = line.replace('\'', '').replace(' ', '').replace('[', '').replace(']', '').split(',')
        architecture = Point.objects.get(id=int(info[0]))
        start = architecture.inner_points.all()[0].id
        point = Point.objects.get(id=start + i)
        i += 1
        flag = int(info[5])
        if flag == 1:
            door = int(info[6])
            # road = Road.objects.create(long=1e-5, belong_id=info[0])
            # road.points.add(point)
            # road.points.add()
            door = Point.objects.get(id=door)
            door.name = "门"
            door.save()
        # elif flag == 3:
        #     point.name = info[6] + "_" + info[7] + "_" + info[8]
        #     point.save()

    # pid.close()
    # pid = open(os.path.join('architecture', 'zip', path, "buildingId_id1_id2_dist.txt"), encoding="utf-8")
    # lines = pid.readlines()
    # for line in lines:
    #     info = line.replace('\'', '').replace(' ', '').replace('[', '').replace(']', '').split(',')
    #     architecture = Point.objects.get(id=int(info[0]))
    #     start = architecture.inner_points.all()[0].id
    #     point1 = architecture.inner_points.get(id=int(info[1]) + start - 1)
    #     point2 = architecture.inner_points.get(id=int(info[2]) + start - 1)
    #     road = Road.objects.create(long=float(info[3]), belong_id=info[0])
    #
    #     road.points.add(point1)
    #     road.points.add(point2)
    # pid.close()


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


if Point.objects.count() == 0:
    Point.objects.create(name="沙河")
    Point.objects.create(name="西土城")
    import_data("沙河")
    import_data("西土城")
    import_architecture("final")
    import_architecture("楼内1")
    import_architecture("楼内2")
    import_architecture("楼内3")
floyd()
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


def import_picture():
    files = os.listdir(settings.IMAGE_DIR)
    for file_name in files:
        ids = file_name.replace('.svg', '').split('_')
        for pid in ids:
            item = Point.objects.get(id=pid)
            item.img = 'http://127.0.0.1:8000/image/{}'.format(file_name)
            item.save()

# import_picture()
