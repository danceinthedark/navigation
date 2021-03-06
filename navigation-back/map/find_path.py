import random
from math import *

from .models import Point, Road

change_list = []

def obtain_road(root):
    # 获取以root为根的地图的拥挤度
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
                link.append({"source": str(x), "target": str(item['x']), 'value': 1-item['rate']})
    return nodes, link

def store():
    # 将随机后的拥挤度数据写入数据库
    global change_list
    for item in change_list:
        edge = Road.objects.filter(points=item[0]).filter(points=item[1])[0]
        edge.rate = item[3]
        edge.save()


def random_road():
    # 随机化拥挤度
    global change_list
    n = Point.objects.get(id=1).inner_points.count() + Point.objects.get(id=2).inner_points.count()
    for i in range(100):
        x = random.randint(1, n)  # 随机选择一个校区内节点
        while len(f[x]) == 0:
            x = random.randint(1, n)
        y = random.randint(1, len(f[x])) - 1  # 随机选择与该节点相连的一条边
        z = f[x][y]['x']
        rate = random.random()
        f[x][y]['rate'] = rate
        for j in range(len(f[z])):
            if f[z][j]['x'] == x:
                f[z][j]['rate'] = rate
                break
        change_list.append((x, z, rate))


def is_on(x, y, z, point0, point1):
    # 通过向量内积判断(x,y,z)是否在point0和point1相连的线段上
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
    return (x0 * x1 + y0 * y1) <= -0.8*(len0 * len1)


def sqr(x):
    return x * x


def eucid_distance(x, y, z, approach_point):
    approach_point = points[approach_point]
    return sqrt(sqr(approach_point['x'] - x) + sqr(approach_point['y'] - y))


def eucid_time(x, y, z, point, speeds):
    long = eucid_distance(x, y, z, point)
    for road in f[point]:
        if is_on(x, y, z, point, road['x']):
            return [long / (speeds[road['type']] * road['rate']), road['type']]
    return 0


def dijkstra(start_point):
    # 从start_point为起始点进行dijkstra算法
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
    # 初始化，将数据库内的数据缓存至内存
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
    # 计算每一张地图的大小
    for i in range(n):
        if mxx[i] < mix[i]:
            continue
        x = (mxx[i] - mix[i]) / 900
        y = (mxy[i] - miy[i]) / 900
        scale[i] = 2 * sqrt(x * x + y * y)
    for road in Road.objects.all():
        [p1, p2] = road.points.all()
        f[p1.id].append({"x": p2.id, "long": road.long, "rate": road.rate, "type": road.type})
        f[p2.id].append({"x": p1.id, "long": road.long, "rate": road.rate, "type": road.type})


def find_nearer_point(root, x, y, z):
    # 查找root为根的地图下(x,y,z)的相邻节点(在某条边上则返回边的两端，若在节点上则返回节点)
    nearer_points = []
    n = Point.objects.count() + 1
    # 判断(x,y,z)是否在节点上
    for point0 in points[1:-1]:
        if point0['belong'] == root.id and z == point0['z'] \
                and eucid_distance(x, y, z, point0['id']) < scale[root.id]:
            return [point0['id']]
    # 判断(x,y,z)是否在某条边上
    for point0 in range(1, n):
        if points[point0]['belong'] == root.id:
            for edge in f[point0]:
                if is_on(x, y, z, point0, edge['x']):
                    nearer_points.append(point0)
                    nearer_points.append(edge['x'])
                    break
        if len(nearer_points) > 0:
            break
    return nearer_points


'''find开头的dest均位Point类型，其余位id'''


def dijkstra_dist(start_x, start_y, start_z, start_point, dest, speeds, move_model):
    # 最短路径下的dijkstra算法，从起始点(x，y,z)经过地图节点start_point后到达dest的最短路径
    start_point = points[start_point]
    n = Point.objects.count()
    dist = [1e10] * (n + 1)
    cost_time = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)  # 记录更新该点的父节点
    front_path = [0] * (n + 1)  # 记录更新某点的父节点所通过的路径类型
    dist[start_point['id']] = 0
    cost_time[start_point['id']] = 0
    # 进行dijkstra算法
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
                    front_path[y] = road['type'] if move_model == '自行车' else 1
            visit[nearset_point] = 1
    # 从终点一路沿着更新自己的父节点直到树根，所经过的路径即为起点到终点的最短路径
    path = [dest]
    for point in path:
        if point != start_point['id']:
            path.append(front_point[point])
    path.reverse()
    d = eucid_distance(start_x, start_y, start_z, path[0])
    result = []
    total_time = 0
    now_time = 0
    if d > 1e-2:
        types = [eucid_time(start_x, start_y, start_z, start_point['id'], speeds)[1] if move_model == "自行车" else 1]
        path1 = [(start_x, start_y), (start_point['x'], start_point['y'])]
    else:
        types = []
        path1 = [(start_point['x'], start_point['y'])]
    # 沿着最短路径记录每条路径的长度、类型以及所消耗的时间
    for i in range(len(path) - 1):
        s = points[path[i]]
        t = points[path[i + 1]]
        if s['belong'] != t['belong'] or s['z'] != t['z']:
            if len(path1) > 1:
                total_time += now_time
                result.append({"type": 1, "dist": d, "total_time": now_time / 30, "time": types,
                               "z": s['z'], "path": path1, "move_model": move_model, "id": s['belong']})
            types = []
            now_time = 0
            path1 = []
            d = 0
        else:
            d += dist[t['id']] - dist[s['id']]
            now_time += cost_time[t['id']] - cost_time[s['id']]
            types.append(front_path[path[i+1]])
        path1.append((t['x'], t['y']))
    if len(path1) > 1:
        result.append({"type": 1, "dist": d, "total_time": now_time / 30, "time": types,
                       "z": points[path[-1]]['z'], "path": path1, "move_model": move_model,
                       "id": points[path[-1]]['belong']})
        total_time += now_time
    total_time /= 30
    return [result, dist[dest] + eucid_distance(start_x, start_y, start_z, start_point['id']), total_time]


def find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model):
    # 从起始点(start_x,start_y,start_z)到终点dest的最短距离
    # 由于起始点不一定是地图上节点，因此考虑找到起始点的相邻节点，以相邻节点为跳板到达终点，最后距离再加上起始点到相邻节点的距离。
    # 若有2个相邻节点，则取到目的地距离最小的
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    shortest_path = []
    shortest_dist = 1e9
    global all
    # 记录最短路径上可能经过的节点
    all = root.inner_points.all() | dest.belong.inner_points.all()
    if root.id > 2 and root != dest.belong:
        all |= root.belong.inner_points.all()
    all = [i.id for i in all]
    shortest_time = 0
    # 枚举相邻节点，分别以相邻节点为跳板进行到终点的最短路搜索
    for point in nearer_points:
        [path, dist, time] = dijkstra_dist(start_x, start_y, start_z, point, dest.id, speeds, move_model)
        if dist < shortest_dist:
            shortest_path = path
            shortest_dist = dist
            shortest_time = time
    return [shortest_path, shortest_time]


def dijkstra_time(start_x, start_y, start_z, start_point, dest, speeds, move_model):
    # 最短路径下的dijkstra算法，从起始点(x，y,z)经过地图节点start_point后到达dest的最短时间
    start_point = points[start_point]
    n = Point.objects.count()
    time_consuming = [1e10] * (n + 1)
    visit = [0] * (n + 1)
    front_point = [0] * (n + 1)  # 记录更新该点的父节点
    front_path = [0] * (n + 1)  # 记录更新某点的父节点所通过的路径类型
    time_consuming[start_point['id']] = 0
    # 进行dijkstra算法
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
                    front_path[y] = road['type'] if move_model == '自行车' else 1
            visit[nearset_point] = 1
    # 从终点一路沿着更新自己的父节点直到树根，所经过的路径即为起点到终点的最短路径
    path = [dest]
    for point in path:
        if point != start_point['id']:
            path.append(front_point[point])
    path.reverse()
    result = []
    d = eucid_distance(start_x, start_y, start_z, path[0])
    now_time = 0
    if d > 1e-2:
        types = [eucid_time(start_x, start_y, start_z, start_point['id'], speeds)[1] if move_model == "自行车" else 1]
        path1 = [(start_x, start_y), (start_point['x'], start_point['y'])]
    else:
        types = []
        path1 = [(start_point['x'], start_point['y'])]
    # 沿着最短路径记录每条路径的长度、类型以及所消耗的时间
    for i in range(len(path) - 1):
        s = points[path[i]]
        t = points[path[i + 1]]
        if s['belong'] != t['belong'] or s['z'] != t['z']:
            if len(path1) > 1:
                result.append({"type": 1, "dist": d, "total_time": now_time / 30, "time": types,
                               "z": s['z'], "path": path1, "move_model": move_model if s['belong'] < 3 else "步行",
                               "id": s['belong']})
            types = []
            path1 = []
            now_time = 0
            d = 0
        else:
            d += eucid_distance(s['x'], s['y'], s['z'], path[i + 1])
            now_time += time_consuming[t['id']] - time_consuming[s['id']]
            types.append(front_path[path[i+1]])
        path1.append((t['x'], t['y']))
    if len(path1) > 1:
        result.append({"type": 1, "dist": d, "total_time": now_time / 30, "time": types, "z": points[path[-1]]['z'],
                       "path": path1, "move_model": move_model if points[path[-1]]['belong'] < 3 else "步行",
                       "id": points[path[-1]]['belong']})
    return [result, (time_consuming[dest] + eucid_time(start_x, start_y, start_z, start_point['id'], speeds)[0]) / 30]


def find_path_time(root, start_x, start_y, start_z, dest, speeds, move_model):
    # 从起始点(start_x,start_y,start_z)到终点dest的最短时间
    # 由于起始点不一定是地图上节点，因此考虑找到起始点的相邻节点，以相邻节点为跳板到达终点，最后距离再加上起始点到相邻节点的时间。
    # 若有2个相邻节点，则取到目的地时间最小的
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    shortest_path = []
    shortest_time = 1e9
    global all
    # 记录最短路径上可能经过的节点
    all = root.inner_points.all() | dest.belong.inner_points.all()
    if root.id > 2 and root != dest.belong:
        all |= root.belong.inner_points.all()
    all = [i.id for i in all]
    # 枚举相邻节点，分别以相邻节点为跳板进行到终点的最短路搜索
    for point in nearer_points:
        [path, time] = dijkstra_time(start_x, start_y, start_z, point, dest.id, speeds, move_model)
        if time < shortest_time:
            shortest_path = path
            shortest_time = time
    return [shortest_path, shortest_time]


def dp(root, start_x, start_y, start_z, dest, approach, speeds, move_model):
    # 通过动态规划实现使用最短距离通过所有途径点并最终结束与终点
    # 用二进制S表示路线是否经过途径点，为1表示已经经过
    # 设g[i][S]表示表示当前路线末端为i,经过的途径点状态为S
    # 将终点dest加入途径点列表末端approach[n]，则最后答案路线长度即为g[n][(1<<n)-1]
    root = Point.objects.get(id=root)
    nearer_points = find_nearer_point(root, start_x, start_y, start_z)
    approach.append(dest)
    n = len(approach)
    f = [[1e9 if i != j else 0 for i in range(n)] for j in range(n)]
    g = [[1e9 for i in range(1 << n)] for j in range(n)]
    # 通过对每个途径点使用dijkstra求得到其他途径点的最短距离,记f[i][j]为途径点i到j的最短距离
    # 并求得到起点的最短距离来预处理出g[i][1<<i]
    for i in range(n):
        d = dijkstra(approach[i])
        for point in nearer_points:
            g[i][1 << i] = min(g[i][1 << i], eucid_distance(start_x, start_y, start_z, point) + d[point])
        for j in range(n):
            f[i][j] = d[approach[j]]
    last = [[-1 for i in range(1 << n)] for j in range(n)]
    # 枚举当前状态S，以及路线末端i，并枚举一个未经过的途径点k，利用g[i][S]+f[i][k]来更新g[k][S|(1<<k)]
    for S in range(1 << n):
        for i in range(n):
            if (1 << i) & S:
                for k in range(n):
                    if (1 << k) & S == 0 and g[k][S | (1 << k)] > g[i][S] + f[i][k]:
                        g[k][S | (1 << k)] = g[i][S] + f[i][k]
                        last[k][S | (1 << k)] = i
    # 根据更新路径回溯遍历出完整道路信息
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
        if len(result) == 0:
            result = ans
        else:
            x = ans[-1]
            result[0]['dist'] += x['dist']
            result[0]['total_time'] += x['total_time']
            result[0]['time'] = x['time'] + result[0]['time']
            x['path'].pop()
            result[0]['path'] = x['path'] + result[0]['path']
            ans.pop()
            result = ans + result
        total_time += time
        x = y
    return [result, total_time]


def find_approach_dist(root, start_x, start_y, start_z, dest, approach, speeds, move_model):
    if not len(approach):
        # 若途径点为空则直接进行按最短路径处理
        return find_path_dist(root, start_x, start_y, start_z, dest, speeds, move_model)
    else:
        # 若途径点非空则惊醒动态规划
        return dp(root, start_x, start_y, start_z, dest.id, approach, speeds, move_model)
