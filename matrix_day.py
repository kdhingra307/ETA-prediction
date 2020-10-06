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
import os 
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


def get_start_time(stop_tree):
    for route in stop_tree:
        for trip in stop_tree[route]:
            for e in stop_tree[route][trip]:
                if e != None:
                    return e[0]



for tree_file in glob("assets/processed/stops/*"):
    if os.path.exists("assets/processed/matrix/{}".format(tree_file.split("/")[-1])):
        continue
    
    matrix = np.zeros([len(dictionary), 144]).astype(np.float32)
    count = np.zeros([len(dictionary), 144]).astype(np.float32)
    stop_tree = np.load(tree_file, allow_pickle=True)['arr_0'].item()
    
    route = next(iter(stop_tree.keys()))
    trip_id = next(iter(stop_tree[route].keys()))
    random_time = get_start_time(stop_tree)
    
    current_data = datetime.fromtimestamp(random_time)
    matrix = np.zeros([len(dictionary), 144]).astype(np.float32)
    count = np.zeros([len(dictionary), 144]).astype(np.float32)

    time = current_data.date()
    start_date = int(datetime(year=time.year, month=time.month, day=time.day, hour=0, minute=0, second=0, microsecond=0).timestamp())
    for route_id in stop_tree:
        stops = routes_data[route_id]
        for each_trip in stop_tree[route_id]:

            for start_stop in range(len(stops)-1):
                if stop_tree[route_id][each_trip][start_stop] == None or stop_tree[route_id][each_trip][start_stop+1] == None:
                    continue
                start_time = ((stop_tree[route_id][each_trip][start_stop][0]
                                +stop_tree[route_id][each_trip][start_stop][-1])//2
                            - start_date)
                if start_time < 0:
                    continue
                
                end_time = ((stop_tree[route_id][each_trip][start_stop+1][0] 
                                +stop_tree[route_id][each_trip][start_stop+1][-1])//2
                            - start_date)
                
                if (end_time - start_time) > 1800:
                    continue
                try:
                    matrix[dictionary[stops[start_stop]], start_time//600] += float(end_time - start_time)/60
                    count[dictionary[stops[start_stop]], start_time//600] += 1
                except:
                    print(start_time, start_date, tree_file, stop_tree[route_id][each_trip][start_stop][0])
                    raise
    
    matrix /= count
    matrix[np.isnan(matrix)] = 0
    np.savez_compressed("assets/processed/matrix/{}".format(tree_file.split("/")[-1]), matrix = matrix, day=current_data.weekday(), month = current_data.month, year=current_data.year, date=current_data.day)