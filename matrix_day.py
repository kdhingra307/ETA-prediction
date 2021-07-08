import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob

import gmplot
from utils import (
    get_route_details,
    get_stops_details,
    haversine_dist,
    get_matrix1_map,
)
import os
from random import choice

stops_data = get_stops_details()
routes_data = get_route_details()

matrix1_map = get_matrix1_map(routes_data)


def get_start_time(stop_tree):
    stamp = {}
    for route in stop_tree:
        if np.random.uniform() > 0.9:
            for trip in stop_tree[route]:
                if np.random.uniform() > 0.5:
                    for e in stop_tree[route][trip]:
                        if e != None:
                            current_data = datetime.fromtimestamp(e)
                            time = current_data.date()
                            start_date = int(
                                datetime(
                                    year=time.year,
                                    month=time.month,
                                    day=time.day,
                                    hour=0,
                                    minute=0,
                                    second=0,
                                    microsecond=0,
                                ).timestamp()
                            )
                            if start_date not in stamp:
                                stamp[start_date] = 0
                            else:
                                stamp[start_date] += 1
                        break

    return max(stamp, key=lambda x: stamp[x])


for tree_file in glob("assets/processed/stops_aligned/*"):
    if os.path.exists(
        "assets/processed/matrix_short/{}".format(tree_file.split("/")[-1])
    ):
        continue

    matrix = np.zeros([matrix1_map["size"], 144]).astype(np.float32)
    count = np.zeros([matrix1_map["size"], 144]).astype(np.float32)
    stop_tree = np.load(tree_file, allow_pickle=True)["arr_0"].item()

    start_date = get_start_time(stop_tree)
    error_count = 0
    for route_id in stop_tree:
        stops = routes_data[route_id]
        for each_trip in stop_tree[route_id]:

            for start_stop in range(len(stops) - 1):
                if (
                    stop_tree[route_id][each_trip][start_stop] == None
                    or stop_tree[route_id][each_trip][start_stop + 1] == None
                ):
                    continue

                start_time = (
                    stop_tree[route_id][each_trip][start_stop][-1][0]
                    - start_date
                )
                if start_time < 0:
                    continue

                end_time = (
                    stop_tree[route_id][each_trip][start_stop + 1][0][0]
                    - start_date
                )

                if (
                    (end_time - start_time) > 1800
                    or (end_time - start_time) < 0
                    or (end_time - start_time) < 30
                ):
                    continue
                try:
                    matrix[
                        matrix1_map["map"][stops[start_stop]][
                            stops[start_stop + 1]
                        ],
                        start_time // 600,
                    ] += (
                        float(end_time - start_time) / 60
                    )
                    count[
                        matrix1_map["map"][stops[start_stop]][
                            stops[start_stop + 1]
                        ],
                        start_time // 600,
                    ] += 1
                except:
                    error_count += 1
                    continue

    matrix /= count
    matrix[np.isnan(matrix)] = 0
    np.savez_compressed(
        "assets/processed/matrix_short/{}".format(tree_file.split("/")[-1]),
        matrix=matrix,
    )
    print(
        "Error Count in {}:- {} out of ".format(
            tree_file.split("/")[-1], error_count
        )
    )
# %%
