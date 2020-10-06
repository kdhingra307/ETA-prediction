import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob
## gmplot - dependency to create geoplot
import gmplot
import utils
from random import choice

stops_data = utils.stops_data
routes_data = utils.routes_data
haversine_dist = utils.haversine_dist

dictionary = {}
count = 0
for route_id in routes_data:
    for s1 in utils.routes_data[route_id]:
        if s1 not in dictionary:
            dictionary[s1] = count
            count += 1

for tree_file in tqdm(glob("./assets/processed/tree/*")):
    tree = np.load(tree_file ,allow_pickle=True)['arr_0'].item()
    route = next(iter(tree.keys()))
    trip_id = next(iter(tree[route].keys()))
    random_time = tree[route][trip_id][0][0]
    current_data = datetime.fromtimestamp(random_time)
    matrix = np.zeros([len(dictionary), 144]).astype(np.float32)
    count = np.zeros([len(dictionary), 144]).astype(np.float32)

    time = current_data.date()
    start_date = int(datetime(year=time.year, month=time.month, day=time.day, hour=0, minute=0, second=0, microsecond=0).timestamp())
    
    stop_tree = {}
    for route_id in tree:
        stop_tree[route_id] = {}
        for trip_id in tree[route_id]:
            stop_tree[route_id][trip_id] = [None]*len(utils.routes_data[route_id])

            stop_id = 0
            for each_click in tree[route_id][trip_id]:
                prev_distance = haversine_dist(stops_data[routes_data[route_id][stop_id]][0], stops_data[routes_data[route_id][stop_id]][1],
                                            each_click[2], each_click[3])
                
                for each_stop in range(stop_id+1, len(routes_data[route_id])):
                    cur_distance = haversine_dist(stops_data[routes_data[route_id][each_stop]][0], stops_data[routes_data[route_id][each_stop]][1],
                                                each_click[2], each_click[3])
                    if cur_distance < prev_distance:
                        prev_distance = cur_distance
                        stop_id = each_stop
                    else:
                        break
                
                if prev_distance < 100:
                    if stop_tree[route_id][trip_id][stop_id] == None:
                        stop_tree[route_id][trip_id][stop_id] = []
                    stop_tree[route_id][trip_id][stop_id].append(each_click)
    print(stop_tree.keys())
    break