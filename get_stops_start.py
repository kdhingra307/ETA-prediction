from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from scipy import interpolate
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob


from utils import (
    get_route_details,
    get_stops_details,
    haversine_dist,
    cartesian,
)
import os
from random import choice
from bisect import bisect_left

stops_data = get_stops_details()
routes_data = get_route_details()


def get_angle(coor1, coor2):
    return np.dot(coor1, coor2) / (
        np.linalg.norm(coor1) * np.linalg.norm(coor2)
    )


def longest_subsequence(seq, return_index=False):

    bisect = bisect_left

    rank = list(seq)

    if not rank:
        return []

    lastoflength = [0]  # end position of subsequence with given length
    predecessor = [
        None
    ]  # penultimate element of l.i.s. ending at given position

    for i in range(1, len(seq)):
        # seq[i] can extend a subsequence that ends with a lesser (or equal) element
        j = bisect([rank[k] for k in lastoflength], rank[i])
        # update existing subsequence of length j or extend the longest
        try:
            lastoflength[j] = i
        except:
            lastoflength.append(i)
        # remember element before seq[i] in the subsequence
        predecessor.append(lastoflength[j - 1] if j > 0 else None)

    def trace(i):
        if i is not None:
            yield from trace(predecessor[i])
            yield i

    indices = trace(lastoflength[-1])

    return list(indices) if return_index else [seq[i] for i in indices]


def task(tree_file):
    if os.path.exists(
        "assets/processed/stops_aligned/{}".format(tree_file.split("/")[-1])
    ):
        print("passed", tree_file)
        return

    try:
        tree = np.load(tree_file, allow_pickle=True)["arr_0"].item()
    except:
        print(tree_file)

    stop_tree = {}

    for route_id in tqdm(tree):
        stops = routes_data[route_id]
        stop_tree[route_id] = {}

        directions = []
        for e in range(1, len(stops)):
            directions.append(
                cartesian(*stops_data[stops[e]][:2])
                - cartesian(*stops_data[stops[e - 1]][:2])
            )

        for each_trip in stop_tree[route_id]:
            stop_tree[route_id][each_trip] = [None] * len(stops)

            for start_stop in range(0, len(stops)):

                if stop_tree[route_id][each_trip][start_stop] == None:
                    continue

                trip_stop_data = np.array(
                    stop_tree[route_id][each_trip][start_stop]
                )

                if (
                    len(trip_stop_data) > 1
                    and (np.diff([e[0] for e in trip_stop_data]) < 0).any()
                ):
                    if (
                        np.count_nonzero(
                            np.diff([e[0] for e in trip_stop_data]) < 0
                        )
                        > 1
                    ):
                        continue
                    else:
                        trip_stop_data = sorted(
                            trip_stop_data, key=lambda e: e[0]
                        )

                _, un_repeat_stops = np.unique(
                    [e[0] for e in trip_stop_data], return_index=True
                )

                trip_stop_data = np.array(trip_stop_data)[un_repeat_stops]

                assert (np.diff([e[0] for e in trip_stop_data]) > 0).all()

                distances = np.array(
                    [
                        haversine_dist(
                            *e[2:], *stops_data[stops[start_stop]][:2]
                        )
                        for e in trip_stop_data
                    ]
                )

                time = np.array([e[0] for e in trip_stop_data])
                close_time = np.argmin(distances)
                close_time_val = time[close_time]

                time -= time[close_time]

                max_range = np.zeros(len(time), dtype=bool)
                max_range[-15 + close_time : close_time] = True
                max_range[close_time : close_time + 15] = True
                useful_indices = np.logical_and(
                    np.logical_and(time < 5 * 60, time > -5 * 60), max_range
                )
                time = time[useful_indices]
                distances = distances[useful_indices]
                trip_stop_data = trip_stop_data[useful_indices]

                if start_stop == 0:
                    prev_dir = -1 * directions[0]
                    next_dir = directions[0]
                elif start_stop == len(stops) - 1:
                    prev_dir = -1 * directions[len(stops) - 2]
                    next_dir = directions[len(stops) - 2]
                else:
                    prev_dir = -1 * directions[start_stop - 1]
                    next_dir = directions[start_stop]

                prev_dir = np.array(
                    [
                        get_angle(
                            prev_dir,
                            cartesian(*e[2:])
                            - cartesian(*stops_data[stops[start_stop]][:2]),
                        )
                        for e in trip_stop_data
                    ]
                )
                next_dir = np.array(
                    [
                        get_angle(
                            next_dir,
                            cartesian(*e[2:])
                            - cartesian(*stops_data[stops[start_stop]][:2]),
                        )
                        for e in trip_stop_data
                    ]
                )

                backward = prev_dir > next_dir

                displacement = distances * (-1 * (backward - 0.5) * 2)

                useful_indices = longest_subsequence(
                    displacement, return_index=True
                )
                displacement = displacement[useful_indices]
                time = time[useful_indices]
                trip_stop_data = trip_stop_data[useful_indices]

                if (
                    len(displacement) > 1
                    and -32 > displacement[0]
                    and -32 < displacement[-1]
                ):
                    stop_tree[route_id][each_trip][start_stop] = int(
                        close_time_val
                        + interpolate.interp1d(
                            displacement, time, fill_value="extrapolate"
                        )(-32)
                    )
                elif len(displacement) > 1:
                    dist_diff = np.diff(displacement)
                    drequired = (
                        displacement[0] + 32
                        if displacement[0] > -32
                        else displacement[-1] + 32
                    )
                    velocity_ind = np.argmin(np.abs(dist_diff - drequired))
                    velocity = dist_diff[velocity_ind] / (
                        time[velocity_ind + 1] - time[velocity_ind]
                    )

                    trequired = (
                        time[0] - drequired / velocity
                        if displacement[0] > -32
                        else time[-1] + drequired / velocity
                    )

                    stop_tree[route_id][each_trip][start_stop] = int(
                        close_time_val + trequired
                    )
                else:
                    assert len(displacement) == 1
                    speed = trip_stop_data[0][1] * 3.6
                    drequired = displacement[0] + 32

                    if speed == 0:
                        speed = 2.7

                    trequired = (
                        time[0] - drequired / speed
                        if displacement[0] > -32
                        else time[-1] + drequired / speed
                    )
                    stop_tree[route_id][each_trip][start_stop] = int(
                        close_time_val + trequired
                    )

    np.savez_compressed(
        "assets/processed/stops_aligned/{}".format(tree_file.split("/")[-1]),
        stop_tree,
    )


executor = ThreadPoolExecutor(max_workers=8)
list(tqdm(map(task, glob("./assets/processed/stops_super/*"))))
