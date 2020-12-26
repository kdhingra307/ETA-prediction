from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob

import gmplot
from utils import get_route_details, get_stops_details,haversine_dist
import os
from random import choice

stops_data = get_stops_details()
routes_data = get_route_details()


def task(tree_file):
    if os.path.exists("assets/processed/stops_with_speed/{}".format(tree_file.split("/")[-1])):
        return
    
    try:
        tree = np.load(tree_file, allow_pickle=True)['arr_0'].item()
    except:
        print(tree_file)

    stop_tree = {}
    for route_id in tree:
        stop_tree[route_id] = {}
        for trip_id in tree[route_id]:
            stop_tree[route_id][trip_id] = [None] * \
                len(routes_data[route_id])

            stop_id = 0
            for each_click in tree[route_id][trip_id]:
                prev_distance = haversine_dist(stops_data[routes_data[route_id][stop_id]][0],
                                               stops_data[routes_data[route_id][stop_id]][1],
                                               each_click[2], each_click[3])

                for each_stop in range(stop_id+1, len(routes_data[route_id])):
                    cur_distance = haversine_dist(stops_data[routes_data[route_id][each_stop]][0],
                                                  stops_data[routes_data[route_id][each_stop]][1],
                                                  each_click[2], each_click[3])
                    if cur_distance < prev_distance:
                        prev_distance = cur_distance
                        stop_id = each_stop
                    else:
                        break

                if prev_distance < 200:
                    if stop_tree[route_id][trip_id][stop_id] == None:
                        stop_tree[route_id][trip_id][stop_id] = []
                    stop_tree[route_id][trip_id][stop_id].append(
                        (each_click[0], each_click[1]))
    np.savez_compressed(
        "assets/processed/stops_with_speed/{}".format(tree_file.split("/")[-1]), stop_tree)


executor = ThreadPoolExecutor(max_workers=8)
list(tqdm(map(task, glob("./assets/processed/tree/*"))))
