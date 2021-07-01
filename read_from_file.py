from datetime import datetime
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np


def load_file(file_name):
    import sqlite3
    db = sqlite3.connect(file_name)
    
    speed_data = db.execute(
        "Select timestamp, route_id, trip_id, lat, lng from vehicle_feed")

    return speed_data

# def live_feed():
#     from google.transit import gtfs_realtime_pb2
#     import requests
#     url = "http://dtcbuses.chartr.in/pb/VehiclePositions.pb?key=Dzfqplgrn3ZfyvAyJjSnpGx3oZZOG20m"
#     feed = gtfs_realtime_pb2.FeedMessage()

#     def fetch():
#         response = requests.get(url).content
#         feed.ParseFromString(response)








def initialize(file=None, live=False):

    if not live and file is None:
        raise ValueError("Need historical file or livefeed ")
    
    if file:
        return load_file(file)


def add_to_tree(time_tree, feed):
    time = int(feed[0])
    route_id = int(feed[1])
    trip_id = feed[2]
    lat = float(feed[3])
    lng = float(feed[4])

    time_lag = int((time - start_time)/10)

    if time_lag < 0:
        return
    
    tree = time_tree[time_lag]

    if route_id not in tree:
        tree[route_id] = {}
    
    if trip_id not in tree[route_id]:
        tree[route_id][trip_id] = []
        tree[route_id][trip_id].append((time, lat, lng))
        
    if tree[route_id][trip_id][-1][0] > time:
        raise ValueError("Current time cant be less than previous for a trip")
    elif tree[route_id][trip_id][-1][0] < time:
        tree[route_id][trip_id].append((time, lat, lng))
#%%
def get_current_time():
    stuff = start_time.replace(hour=np.random.randint(9, 18), minute=np.random.randint(60), second=np.random.randint(60))
    return stuff

route_data = get_route_details()
stop_data = get_stops_details()

def get_start_stops(time_tree):

    bus_at_stops = {e:[] for e in stop_data}
    current_time = get_current_time()
    time_lag = int((current_time.timestamp() - start_time.timestamp())/10)
    locations = time_tree[time_lag]

    for each_route_id in tqdm(locations):
        for each_stop in route_data[each_route_id]:
            stop_coord = stop_data[each_stop][:2]
            for each_trip_id in locations[each_route_id]:
                for each_entry in locations[each_route_id][each_trip_id]:
                    if haversine_dist(*stop_coord, *each_entry[1:]) < 20:
                        bus_at_stops[each_stop].append([each_route_id, each_trip_id, each_entry[0]])
                        break

    best_stop = sorted(bus_at_stops, key=lambda e:-1*len(bus_at_stops[e]))[0]
    return best_stop, current_time, bus_at_stops[best_stop]


def get_time_tree():

    data = initialize()
    time_tree = [{} for _ in range(8640)]
    for e in tqdm(data):
        add_to_tree(time_tree, e)

    return time_tree

def location(timetree, time, route_id, trip_id):
    time_lag = int((time - start_time.timestamp())/10)
    locations = timetree[time_lag]
    trip_data = timetree[route_id][trip_id]
    return trip_data[0]