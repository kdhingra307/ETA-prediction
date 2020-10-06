import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob
import os
import gmplot
import utils
from random import choice

stops_data = utils.stops_data
routes_data = utils.routes_data
haversine_dist = utils.haversine_dist
logger = open("logs/processed/tree.txt", "w")

for each_day in tqdm(glob("/Users/karan/Downloads/bus_movements_2020_08/*")):
    if os.path.exists("assets/processed/tree/{}.npz".format("-d-".join(each_day.split("/")[-2:]))):
        continue

    db = sqlite3.connect(each_day)
    try:
        speed_data = db.execute("Select speed, timestamp, route_id, trip_id, lat, lng from vehicle_feed")
    except:
        logger.write("file: {}, no content found")
        continue
    count_same = 0
    tree = {}
    for e in speed_data:
        try:
            route_id = int(e[2])
            trip_id = e[3]
            time = int(e[1])
            speed = float(e[0])
            lat = float(e[-2])
            lng = float(e[-1])

            if route_id not in tree:
                tree[route_id]  = {}
            
            if trip_id not in tree[route_id]:
                tree[route_id][trip_id]  = [[time, speed, lat, lng]]
            elif time != tree[route_id][trip_id][-1][0]:
                tree[route_id][trip_id].append([time, speed, lat, lng])
        except ValueError as _:
            logger.write("file: {}, row : {}".format(each_day, e))

    np.savez_compressed("assets/processed/tree/{}".format("-d-".join(each_day.split("/")[-2:])), tree)

logger.flush()