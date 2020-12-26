import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob
import os
import gmplot
from utils import get_route_details, get_stops_details, haversine_dist
from random import choice

stops_data = get_stops_details()
routes_data = get_stops_details()

logger = open("logs/processed/tree.txt", "w")

for each_day in tqdm(glob("./dbs/*/*")):
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