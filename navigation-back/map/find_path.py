import collections
from math import *

from .models import Point


def is_on(x, y, road):
    [point0, point1] = road.points.all()
    return abs((y - point0.y) * (point1.x - point0.x) - (point1.y - point0.y) * (x - point0.x)) < 1e-5


def sqr(x):
    return x * x


def eucid_distance(x, y, approach_point):
    return sqrt(sqr(approach_point.x - x) + sqr(approach_point.y - y))


dist = {}


def floyd(last, campus):
    last += 1
    n = last + campus.points.count()
    global dist
    if campus in dist:
        return
    g = [1e9 for i in range(n)]
    f = [g[:] for j in range(n)]
    for k in range(last, n):
        f[k][k] = 0
    for road in campus.roads.all():
        point0 = road.points.all()[0].id
        point1 = road.points.all()[1].id
        f[point0][point1] = f[point1][point0] = road.long

    for k in range(last, n):
        for i in range(last, n):
            for j in range(last, n):
                f[i][j] = min(f[i][k] + f[k][j], f[i][j])
    dist[campus] = f


def eucid_time(x, y, approach_point, speeds):
    long = eucid_distance(x, y, approach_point)
    for road in approach_point.edges.all():
        if is_on(x, y, road):
            return long / (speeds[road.type] * road.rate)
    return 0


def cal(campus, x, y, approach_point, dest):
    return eucid_distance(x, y, approach_point) + dist[campus][approach_point.id][dest.id]


def find_nearer_point(campus, start_x, start_y):
    nearer_points = []
    for road in campus.roads.all():
        if is_on(start_x, start_y, road):
            for point in road.points.all():
                nearer_points.append(point)
    c = collections.Counter(nearer_points)
    most_common = c.most_common(1)[0]
    if most_common[1] > 1:
        nearer_points = [most_common[0]]
    return nearer_points


def find_path_dist(campus, start_x, start_y, dest, speeds):
    nearer_points = find_nearer_point(campus, start_x, start_y)
    nearest_point = nearer_points[0]
    nearest_dist = cal(campus, start_x, start_y, nearest_point, dest)
    for point in nearer_points:
        if cal(campus, start_x, start_y, point, dest) < nearest_dist:
            nearest_dist = cal(campus, start_x, start_y, point, dest)
            nearest_point = point
    path = []
    # for point in campus.points.all():
    #     if abs(dist[campus][nearest_point.id][dest.id] - (
    #             dist[campus][nearest_point.id][point.id] + dist[campus][point.id][dest.id])) < 1e-7:
    #         path.append(point)
    # path.sort(key=lambda x: dist[campus][nearest_point.id][x.id])
    #
    # time = eucid_time(start_x, start_y, path[0], speeds)
    # for i in range(len(path) - 1):
    #     s = path[i]
    #     t = path[i + 1]
    #     edge = campus.roads.filter(points=s).filter(points=t)[0]
    #     time += edge.long / (speeds[edge.type] * edge.rate)
    time = eucid_time(start_x, start_y, nearest_point, speeds)
    x = nearest_point
    path.append(x.id)
    while x != dest:
        for edge in x.edges.all():
            y = edge.points.exclude(id=x.id)[0]
            if abs(dist[campus][nearest_point.id][dest.id] -
                   (dist[campus][nearest_point.id][y.id] + dist[campus][y.id][dest.id])) < 1e-7 and \
                dist[campus][nearest_point.id][x.id]<dist[campus][nearest_point.id][y.id]:
                x = y
                time += edge.long / (speeds[edge.type] * edge.rate)
                break
        path.append(x.id)
    return {'path': path, 'dist': cal(campus, start_x, start_y, nearest_point, dest), 'time': time}


def dijkstra_time(campus, start_x, start_y, start_point, dest, speeds):
    n = Point.objects.count()
    time_consuming = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)
    time_consuming[start_point.id] = 0
    for round in range(n):
        nearset_point = 0
        for point in range(1, n + 1):
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
    path = [campus.points.get(id=item) for item in path]
    dist = eucid_distance(start_x, start_y, path[0])
    for i in range(len(path) - 1):
        s = path[i]
        t = path[i + 1]
        edge = campus.roads.filter(points=s).filter(points=t)[0]
        dist += edge.long
    return [path, dist, time_consuming[dest.id] + eucid_time(start_x, start_y, start_point, speeds)]


def find_path_time(campus, start_x, start_y, dest, speeds):
    nearer_points = find_nearer_point(campus, start_x, start_y)
    shortest_path = []
    shortest_time = 1e9
    shortest_dist = 1e9
    for point in nearer_points:
        [path, dist, time] = dijkstra_time(campus, start_x, start_y, point, dest, speeds)
        if time < shortest_time:
            shortest_path = path
            shortest_time = time
            shortest_dist = dist
    shortest_path = [item.id for item in shortest_path]
    return {'path': shortest_path, 'dist': shortest_dist, 'time': shortest_time}


def floyd_dp(campus, start_x, start_y, dest, approach, speeds):
    nearer_points = find_nearer_point(campus, start_x, start_y)
    approach.append(dest.id)
    n = len(approach)
    f = [[1e9 if i != j else 0 for i in range(n)] for j in range(n)]
    g = [[1e9 for i in range(1 << n)] for j in range(n)]
    for point in nearer_points:
        for point_id in range(n):
            g[point_id][1 << point_id] = min(g[point_id][1 << point_id],
                                             cal(campus, start_x, start_y, point,
                                                 campus.points.get(id=approach[point_id])))
    for i in range(n):
        for j in range(n):
            f[i][j] = dist[campus][approach[i]][approach[j]]

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
    result = {}
    while x >= 0:
        y = last[x][q]
        if y >= 0:
            point = campus.points.get(id=approach[y])
            point = [point.x, point.y]
        else:
            point = [start_x, start_y]
        q ^= 1 << x
        ans = find_path_dist(campus, point[0], point[1], Point.objects.get(id=approach[x]), speeds)
        ans['path'].reverse()
        if 'path' not in result:
            result = ans
        else:
            result['path'].pop()
            result['path'] += ans['path']
            result['dist'] += ans['dist']
            result['time'] += ans['time']
        x = y
    result['path'].reverse()
    return result


def find_approach_dist(campus, start_x, start_y, dest, approach, speeds):
    if not len(approach):
        return find_path_dist(campus, start_x, start_y, dest, speeds)
    else:
        return floyd_dp(campus, start_x, start_y, dest, approach, speeds)
