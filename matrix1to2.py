import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from tqdm import tqdm
from datetime import datetime
from random import choice
from glob import glob
## gmplot - dependency to create geoplot
import gmplot
from utils import get_route_details, get_stops_details
import os 
from random import choice

stops_data = get_stops_details()
routes_data = get_route_details()

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


def map(i1, i2, length):
    return int(i1*(2*length-i1-3)/2 + i2)


def m1to2(matrix1, route_id):
    assert route_id in routes_data
    stops = routes_data[route_id]
    num_stops = len(stops)
    matrix2 = np.zeros([int((num_stops*(num_stops-1))/2)+1, matrix1.shape[1]])
    print(matrix2.shape)

    for i in range(1, num_stops):
        matrix2[map(i-1, i, num_stops)] = matrix1[matrix1_map[stops[i-1][i]]]
        for j in range(i-2, -1, -1):
            prev_time = matrix2[map(j, i-1, num_stops)]
            for k in range(matrix1.shape[1]):
                if prev_time[k] == 0:
                    continue
                
                ind = int(k + matrix1[i-1][k]//10)
                assert ind < matrix1.shape[1]

                matrix2[map(j, i, num_stops), ind] = prev_time[k] + matrix1[matrix1_map[stops[i-1][i]], ind]
                
    return matrix2


matrix1 = np.load("./assets/processed/matrix/bus_movements_2020_08-d-bus_movements_2020_08_05.db.npz")['matrix']

matrix2 = m1to2(matrix1, 534)

np.savez_compressed("./assets/processed/matrix2/bus_movements_2020_08-d-bus_movements_2020_08_05.db.npz", matrix = matrix2)