from math import *

from .models import Point, Road


def is_on(x, y, z, road):
    [point0, point1] = road.points.all()
    if point0.z != z or point1.z != z:
        return 0
    return abs((y - point0.y) * (point1.x - point0.x) - (point1.y - point0.y) * (x - point0.x)) < 1e-5


def sqr(x):
    return x * x


def eucid_distance(x, y, z, approach_point):
    return sqrt(sqr(approach_point.x - x) + sqr(approach_point.y - y) + sqr(approach_point.z - z))


def eucid_time(x, y, z, approach_point, speeds):
    long = eucid_distance(x, y, z, approach_point)
    for road in approach_point.edges.all():
        if is_on(x, y, z, road):
            return long / (speeds[road.type] * road.rate)
    return 0


def dijkstra(start_point):
    n = Point.objects.count()
    d = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    d[start_point.id] = 0
    if start_point.edges.count() == 0:
        return d
    for round in range(n):
        nearset_point = 0
        for point in range(1, n + 1):
            if visit[point] == 0 and d[nearset_point] > d[point]:
                nearset_point = point
        if nearset_point == 0:
            break
        for item in f[nearset_point]:
            if d[item[0]] > d[nearset_point] + item[1]:
                d[item[0]] = d[nearset_point] + item[1]
        visit[nearset_point] = 1
    return d


def floyd():
    global dist
    global f
    n = Point.objects.count() + 1
    f = [[] for i in range(n)]
    for road in Road.objects.all():
        [p1, p2] = road.points.all()
        f[p1.id].append((p2.id, road.long))
        f[p2.id].append((p1.id, road.long))
    dist = [[]]
    default = [1e10] * n
    for item in Point.objects.all():
        if len(item.name) > 0:
            dist.append(dijkstra(item))
        else:
            dist.append(default)


def cal(x, y, z, approach_point, dest):
    return eucid_distance(x, y, z, approach_point) + dist[dest.id][approach_point.id]


def find_nearer_point(root, start_x, start_y, start_z):
    nearer_points = []
    for road in root.inner_roads.all():
        if is_on(start_x, start_y, start_z, road):
            for point in road.points.all():
                nearer_points.append(point)
                if eucid_distance(start_x, start_y, start_z, point) < 1e-7:
                    return [point]
            break
    return nearer_points


def find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model):
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    nearest_point = nearer_points[0]
    nearest_dist = cal(start_x, start_y, start_z, nearest_point, dest)
    for point in nearer_points:
        if cal(start_x, start_y, start_z, point, dest) < nearest_dist:
            nearest_dist = cal(start_x, start_y, start_z, point, dest)
            nearest_point = point
    path = []
    total_time = 0
    time = [eucid_time(start_x, start_y, start_z, nearest_point, speeds)]
    d = eucid_distance(start_x, start_y, start_z, nearest_point)
    path.append((start_x, start_y, start_z))
    x = nearest_point
    path.append((x.x, x.y, x.z))
    result = []
    while x != dest:
        for edge in x.edges.all():
            y = edge.points.exclude(id=x.id)[0]
            if abs(dist[dest.id][x.id] - (edge.long + dist[dest.id][y.id])) < 1e-7:
                if x.belong != y.belong:
                    result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time, "path": path,
                                   "move_model": move_model})
                    total_time += sum(time)
                    d = 0
                    time = []
                    path = []
                else:
                    time.append(edge.long / (speeds[edge.type] * edge.rate))
                    d += edge.long
                x = y
                break
        path.append((x.x, x.y, x.z))
    result.append({"type": 1, "dist": d, "total_time": sum(time), "time": time, "path": path, "move_model": move_model})
    total_time += sum(time)
    return [result, total_time]


def dijkstra_time(start_x, start_y, start_z, start_point, dest, speeds, move_model):
    n = Point.objects.count()
    time_consuming = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)
    time_consuming[start_point.id] = 0
    all = start_point.belong.inner_points.all() | dest.belong.inner_points.all()
    all = [i.id for i in all]
    for round in range(n):
        nearset_point = 0
        for point in all:
            if not visit[point]:
                if time_consuming[nearset_point] > time_consuming[point]:
                    nearset_point = point
        if nearset_point == 0 or nearset_point == dest.id:
            break
        else:
            point = Point.objects.get(id=nearset_point)
            for road in point.edges.all():
                for connect_point in road.points.all():
                    if time_consuming[connect_point.id] > time_consuming[point.id] + road.long / \
                            (speeds[road.type] * road.rate):
                        time_consuming[connect_point.id] = time_consuming[point.id] + road.long / \
                                                           (road.rate * speeds[road.type])
                        front_point[connect_point.id] = point.id
            visit[nearset_point] = 1

    path = [dest.id]
    for point in path:
        if point != start_point.id:
            path.append(front_point[point])
    path.reverse()
    path = [Point.objects.get(id=item) for item in path]
    d = eucid_distance(start_x, start_y, start_z, path[0])
    time = [eucid_time(start_x, start_y, start_z, start_point, speeds)]
    result = []
    path1 = [(start_x, start_y, start_z), (start_point.x, start_point.y, start_point.z)]
    for i in range(len(path) - 1):
        s = path[i]
        t = path[i + 1]
        edge = (s.edges.all() & t.edges.all())[0]
        if s.belong != t.belong:
            result.append(
                {"type": 1, "dist": d, "total_time": sum(time), "time": time, "path": path1, "move_model": move_model})
            time = []
            path1 = [(t.x, t.y, t.z)]
            d = 0
        else:
            d += edge.long
            time.append(time_consuming[t.id] - time_consuming[s.id])
            path1.append((t.x, t.y, t.z))

    result.append(
        {"type": 1, "dist": d, "total_time": sum(time), "time": time, "path": path1, "move_model": move_model})
    return [result, time_consuming[dest.id] + eucid_time(start_x, start_y, start_z, start_point, speeds)]


def find_path_time(root, start_x, start_y, start_z, dest, speeds, move_model):
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    shortest_path = []
    shortest_time = 1e9
    for point in nearer_points:
        [path, time] = dijkstra_time(start_x, start_y, start_z, point, dest, speeds, move_model)
        if time < shortest_time:
            shortest_path = path
            shortest_time = time
    return [shortest_path, shortest_time]


def floyd_dp(root, start_x, start_y, start_z, dest, approach, speeds, move_model):
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    approach.append(dest.id)
    n = len(approach)
    f = [[1e9 if i != j else 0 for i in range(n)] for j in range(n)]
    g = [[1e9 for i in range(1 << n)] for j in range(n)]
    for point in nearer_points:
        for point_id in range(n):
            g[point_id][1 << point_id] = min(g[point_id][1 << point_id],
                                             cal(start_x, start_y, start_z, point,
                                                 Point.objects.get(id=approach[point_id])))
    for i in range(n):
        for j in range(n):
            f[i][j] = dist[approach[i]][approach[j]]

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
    root = Point.objects.get(id=root)
    if not len(approach):
        return find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model)
    else:
        return floyd_dp(root, start_x, start_y, start_z, dest, approach, speeds, move_model)
