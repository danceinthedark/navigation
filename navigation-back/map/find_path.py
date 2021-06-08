import random
from math import *

from .models import Point, Road

change_list = []

def obtain_road(root):
    nodes = []
    points = []
    for point in root.inner_points.all():
        if len(f[point.id]) > 0:
            nodes.append({'name': str(point.id), 'value': [point.x, point.y]})
            points.append(point.id)
    n = Point.objects.count() + 1
    node = [0] * n
    link = []
    for i in points:
        node[i] = 1
    for x in points:
        for item in f[x]:
            if node[item['x']] > 0 and item['x'] > x:
                link.append({"source": str(x), "target": str(item['x']), 'value': item['rate']})
    return nodes, link

def store():
    global change_list
    for item in change_list:
        edge = Road.objects.filter(points=item[0]).filter(points=item[1])[0]
        edge.rate = item[3]
        edge.save()


def random_road():
    global change_list
    n = Point.objects.count()
    for i in range(20):
        x = random.randint(1, n)
        while len(f[x]) == 0:
            x = random.randint(1, n)
        y = random.randint(1, len(f[x])) - 1
        z = f[x][y]['x']
        rate = random.random()
        f[x][y]['rate'] = rate
        for j in range(len(f[z])):
            if f[z][j]['x'] == x:
                f[z][j]['rate'] = rate
                break
        change_list.append((x, z, rate))


def is_on(x, y, z, point0, point1):
    point0 = points[point0]
    point1 = points[point1]
    if point0['z'] != z or point1['z'] != z:
        return 0
    x0 = point0['x'] - x
    y0 = point0['y'] - y
    x1 = point1['x'] - x
    y1 = point1['y'] - y
    len0 = sqrt(sqr(x0) + sqr(y0))
    len1 = sqrt(sqr(x1) + sqr(y1))
    return (x0 * x1 + y0 * y1) / (len0 * len1) < -0.9


def sqr(x):
    return x * x


def eucid_distance(x, y, z, approach_point):
    approach_point = points[approach_point]
    return sqrt(sqr(approach_point['x'] - x) + sqr(approach_point['y'] - y))


def eucid_time(x, y, z, point, speeds):
    long = eucid_distance(x, y, z, point)
    for road in f[point]:
        if is_on(x, y, z, point, road['x']):
            return long / (speeds[road['type']] * road['rate'])
    return 0


# start_point
def dijkstra(start_point):
    n = Point.objects.count()
    d = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    d[start_point] = 0
    for round in range(n):
        nearset_point = 0
        for point in range(1, n + 1):
            if visit[point] == 0 and d[nearset_point] > d[point]:
                nearset_point = point
        if nearset_point == 0:
            break
        for item in f[nearset_point]:
            if d[item['x']] > d[nearset_point] + item['long']:
                d[item['x']] = d[nearset_point] + item['long']
        visit[nearset_point] = 1
    return d


def init():
    global f
    global points
    global scale
    n = Point.objects.count() + 1
    f = [[] for i in range(n)]
    mxy = mxx = [-1e9] * n
    miy = mix = [1e9] * n
    scale = [0] * n
    points = [0]
    for point in Point.objects.all():
        points.append({"id": point.id, "x": point.x, "y": point.y, "z": point.z,
                       "belong": 0 if point.id < 3 else point.belong.id})
        if point.id > 2:
            mxx[point.belong.id] = max(point.x, mxx[point.belong.id])
            mix[point.belong.id] = min(point.x, mix[point.belong.id])
            mxy[point.belong.id] = max(point.y, mxy[point.belong.id])
            miy[point.belong.id] = min(point.y, miy[point.belong.id])

    for i in range(n):
        if mxx[i] < mix[i]:
            continue
        x = (mxx[i] - mix[i]) / 2000
        y = (mxy[i] - miy[i]) / 2000
        scale[i] = 2 * sqrt(x * x + y * y)
    for road in Road.objects.all():
        [p1, p2] = road.points.all()
        f[p1.id].append({"x": p2.id, "long": road.long, "rate": road.rate, "type": road.type})
        f[p2.id].append({"x": p1.id, "long": road.long, "rate": road.rate, "type": road.type})

def find_nearer_point(root, start_x, start_y, start_z):
    nearer_points = []
    n = Point.objects.count() + 1
    for point0 in points[1:-1]:
        if point0['belong'] == root.id and eucid_distance(start_x, start_y, start_z, point0['id']) < scale[root.id]:
                return [point0['id']]
    for point0 in range(1, n):
        if points[point0]['belong'] == root.id:
            for edge in f[point0]:
                if is_on(start_x, start_y, start_z, point0, edge['x']):
                    nearer_points.append(point0)
                    nearer_points.append(edge['x'])
                    break
        if len(nearer_points) > 0:
            break
    return nearer_points


'''find开头的dest均位Point类型，其余位id'''


def dijkstra_dist(start_x, start_y, start_z, start_point, dest, speeds, move_model):
    start_point = points[start_point]
    n = Point.objects.count()
    dist = [1e10] * (n + 1)
    cost_time = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)
    dist[start_point['id']] = 0
    cost_time[start_point['id']] = 0
    for round in range(n):
        nearset_point = 0
        for point in all:
            if not visit[point]:
                if dist[nearset_point] > dist[point]:
                    nearset_point = point
        if nearset_point == 0 or nearset_point == dest:
            break
        else:
            x = nearset_point
            for road in f[x]:
                y = road['x']
                if dist[y] > dist[x] + road['long']:
                    dist[y] = dist[x] + road['long']
                    cost_time[y] = cost_time[x] + road['long'] / (road['rate'] * speeds[road['type']])
                    front_point[y] = x
            visit[nearset_point] = 1

    path = [dest]
    for point in path:
        if point != start_point['id']:
            path.append(front_point[point])
    path.reverse()
    d = eucid_distance(start_x, start_y, start_z, path[0])
    result = []
    if d > 1e-2:
        time = [eucid_time(start_x, start_y, start_z, start_point['id'], speeds)]
        path1 = [(start_x, start_y), (start_point['x'], start_point['y'])]
    else:
        time = []
        path1 = [(start_point['x'], start_point['y'])]
    for i in range(len(path) - 1):
        s = points[path[i]]
        t = points[path[i + 1]]
        if s['belong'] != t['belong'] or s['z'] != t['z']:
            if len(path1) > 1:
                result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time,
                               "z": s['z'], "path": path1, "move_model": move_model, "id": s['belong']})
            time = []
            path1 = []
            d = 0
        else:
            d += dist[t['id']] - dist[s['id']]
            time.append(cost_time[t['id']] - cost_time[s['id']])
        path1.append((t['x'], t['y']))
    if len(path1) > 1:
        result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time,
                       "z": points[path[-1]]['z'], "path": path1, "move_model": move_model,
                       "id": points[path[-1]]['belong']})
    return [result, dist[dest] + eucid_distance(start_x, start_y, start_z, start_point['id'])]


def find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model):
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    shortest_path = []
    shortest_dist = 1e9
    global all
    all = root.inner_points.all() | dest.belong.inner_points.all()
    if root.id > 2  and root != dest.belong:
        all |= root.belong.inner_points.all()
    all = [i.id for i in all]
    for point in nearer_points:
        [path, dist] = dijkstra_dist(start_x, start_y, start_z, point, dest.id, speeds, move_model)
        if dist < shortest_dist:
            shortest_path = path
            shortest_dist = dist
    return [shortest_path, shortest_dist]


def dijkstra_time(start_x, start_y, start_z, start_point, dest, speeds, move_model):
    start_point = points[start_point]
    n = Point.objects.count()
    time_consuming = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)
    time_consuming[start_point['id']] = 0
    for round in range(n):
        nearset_point = 0
        for point in all:
            if not visit[point]:
                if time_consuming[nearset_point] > time_consuming[point]:
                    nearset_point = point
        if nearset_point == 0 or nearset_point == dest:
            break
        else:
            x = nearset_point
            for road in f[x]:
                y = road['x']
                if time_consuming[y] > time_consuming[x] + road['long'] / (road['rate'] * speeds[road['type']]):
                    time_consuming[y] = time_consuming[x] + road['long'] / (road['rate'] * speeds[road['type']])
                    front_point[y] = x
            visit[nearset_point] = 1

    path = [dest]
    for point in path:
        if point != start_point['id']:
            path.append(front_point[point])
    path.reverse()
    result = []
    d = eucid_distance(start_x, start_y, start_z, path[0])
    if d > 1e-2:
        time = [eucid_time(start_x, start_y, start_z, start_point['id'], speeds)]
        path1 = [(start_x, start_y), (start_point['x'], start_point['y'])]
    else:
        time = []
        path1 = [(start_point['x'], start_point['y'])]
    for i in range(len(path) - 1):
        s = points[path[i]]
        t = points[path[i + 1]]
        if s['belong'] != t['belong'] or s['z'] != t['z']:
            if len(path1) > 1:
                result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time,
                               "z": s['z'], "path": path1, "move_model": move_model, "id": s['belong']})
            time = []
            path1 = []
            d = 0
        else:
            d += eucid_distance(s['x'], s['y'], s['z'], path[i + 1])
            time.append(time_consuming[t['id']] - time_consuming[s['id']])
        path1.append((t['x'], t['y']))
    if len(path1) > 1:
        result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time, "z": points[path[-1]]['z'],
                       "path": path1, "move_model": move_model, "id": points[path[-1]]['belong']})
    return [result, time_consuming[dest] + eucid_time(start_x, start_y, start_z, start_point['id'], speeds)]


def find_path_time(root, start_x, start_y, start_z, dest, speeds, move_model):
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    shortest_path = []
    shortest_time = 1e9
    global all
    all = root.inner_points.all() | dest.belong.inner_points.all()
    if root.id > 2 and root != dest.belong:
        all |= root.belong.inner_points.all()
    all = [i.id for i in all]
    for point in nearer_points:
        [path, time] = dijkstra_time(start_x, start_y, start_z, point, dest.id, speeds, move_model)
        if time < shortest_time:
            shortest_path = path
            shortest_time = time
    return [shortest_path, shortest_time]



def floyd_dp(root, start_x, start_y, start_z, dest, approach, speeds, move_model):
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    approach.append(dest)
    n = len(approach)
    f = [[1e9 if i != j else 0 for i in range(n)] for j in range(n)]
    g = [[1e9 for i in range(1 << n)] for j in range(n)]

    for i in range(n):
        d = dijkstra(approach[i])
        for point in nearer_points:
            g[i][1 << i] = min(g[i][1 << i], eucid_distance(start_x, start_y, start_z, point) + d[point])
        for j in range(n):
            f[i][j] = d[approach[j]]

    last = [[-1 for i in range(1 << n)] for j in range(n)]
    for j in range(1 << n):
        for i in range(n):
            if (1 << i) & j:
                for k in range(n):
                    if (1 << k) & j == 0 and g[k][j | (1 << k)] > g[i][j] + f[i][k]:
                        g[k][j | (1 << k)] = g[i][j] + f[i][k]
                        last[k][j | (1 << k)] = i
    x = n - 1
    q = (1 << n) - 1
    result = []
    total_time = 0
    while x >= 0:
        y = last[x][q]
        if y >= 0:
            point = Point.objects.get(id=approach[y])
            zone = point.belong.id
            point = [point.x, point.y, point.z]
        else:
            point = [start_x, start_y, start_z]
            zone = root.id
        q ^= 1 << x
        [ans, time] = find_path_dist(zone, point[0], point[1], point[2], Point.objects.get(id=approach[x]), speeds,
                                     move_model)
        result = ans + result
        total_time += time
        x = y
    return [result, total_time]


def find_approach_dist(root, start_x, start_y, start_z, dest, approach, speeds, move_model):
    if not len(approach):
        return find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model)
    else:
        return floyd_dp(root, start_x, start_y, start_z, dest.id, approach, speeds, move_model)
