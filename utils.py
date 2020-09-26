import numpy as np

to_radian = lambda x : x/57.29577951

def haversine_dist(lat1, lon1, lat2, lon2):
    lat1 = to_radian(lat1)
    lon = to_radian(lon1) - to_radian(lon2)
    lat2 = to_radian(lat2)
    a = np.sin((lat1-lat2) / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(lon / 2)**2
    c = 2*np.arcsin(np.sqrt(a))

    return 6373.0 * c * 1000


stops_data = dict()
i = 0
for e in open("input/static/stops.txt").read().split("\n")[1:-1]:
    split = e.split(",")
    stops_data[int(split[0])] = (float(split[-2]), float(split[-1]), split[0], split[1], i)
    i+=1


trips_data = dict()
for e in open("input/static/stop_times.txt").read().split("\n")[1:-1]:
    split = e.split(",")
    trip_id = split[0]
    if trip_id not in trips_data:
        trips_data[trip_id] = []
    trips_data[trip_id].append((int(split[3]), int(split[-1])))


routes_data = dict()
for e in open("input/static/trips.txt").read().split("\n")[1:-1]:
    split = e.split(",")
    route_id = int(split[0])
    trip_id = split[2]
    if route_id not in routes_data:
        routes_data[route_id] = np.array(sorted(trips_data[trip_id], key=lambda e:e[1]))[:, 0]