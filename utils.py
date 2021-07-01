import numpy as np

version = "1"

def to_radian(x):
    return x/57.29577951

def haversine_dist(lat1, lon1, lat2, lon2):
    lat1 = to_radian(lat1)
    lon = to_radian(lon1) - to_radian(lon2)
    lat2 = to_radian(lat2)
    a = np.sin((lat1-lat2) / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(lon / 2)**2
    c = 2*np.arcsin(np.sqrt(a))

    return 6373.0 * c * 1000

def cartesian(lat, lon):
    return np.array([np.sin(lat)*np.cos(lon), np.sin(lat)*np.sin(lon), np.cos(lat)])


def get_mid_point(lat1, lon1, lat2, lon2):

    lat1 = to_radian(lat1)
    lat2 = to_radian(lat2)
    lon1 = to_radian(lon1)
    lon2 = to_radian(lon2)


    p1 = cartesian(lat1, lon1)
    p2 = cartesian(lat2, lon2)

    mid_point = (p1  + p2)/2

    lon3 = np.arctan(mid_point[1] / mid_point[0])
    lat3 = np.arctan(np.sqrt(mid_point[0]**2 + mid_point[1]**2)/mid_point[2])

    return lat3*57.2957, lon3*57.2957


def get_stops_details():
    stops_data = dict()
    i = 0
    for e in open("input/static/stops_v{}.txt".format(version)).read().split("\n")[1:-1]:
        split = e.split(",")
        stops_data[split[0]] = (float(split[-2]), float(split[-1]), split[0], split[1], i)
        i+=1
    return stops_data


def get_route_details():
    trips_data = dict()
    for e in open("input/static/stop_times_v{}.txt".format(version)).read().split("\n")[1:-1]:
        split = e.split(",")
        trip_id = split[0]
        if trip_id not in trips_data:
            trips_data[trip_id] = []
        trips_data[trip_id].append((split[3], int(split[-1])))


    routes_data = dict()
    for e in open("input/static/trips_v{}.txt".format(version)).read().split("\n")[1:-1]:
        split = e.split(",")
        route_id = int(split[0])
        trip_id = split[2]
        if route_id not in routes_data:
            routes_data[route_id] = np.array(sorted(trips_data[trip_id], key=lambda e:e[1]))[:, 0]
    return routes_data


def get_matrix1_map(routes_data):  
    matrix1_map = {}
    count = 0
    for route_id in routes_data:
        prev_stop = routes_data[route_id][0]
        for next_stop in routes_data[route_id][1:]:
            if prev_stop not in matrix1_map:
                matrix1_map[prev_stop] = {}
            
            if next_stop not in matrix1_map[prev_stop]:
                matrix1_map[prev_stop][next_stop] = count
                count += 1
            
            prev_stop = next_stop
    
    return {
        "map" : matrix1_map,
        "size" : count
    }

def get_matrix2_map(i1, i2, num_stops):
    return int(i1*(2*num_stops-i1-3)/2 + i2)