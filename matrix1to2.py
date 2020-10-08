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

def map(i1, i2, length):
    return int(i1*(2*length-i1-3)/2 + i2)


def m1to2(matrix1, route_id):
    assert route_id in routes_data
    stops = routes_data[route_id]
    num_stops = len(stops)
    matrix2 = np.zeros([int((num_stops*(num_stops-1))/2)+1, matrix1.shape[1]])
    print(matrix2.shape)

    for i in range(1, num_stops):
        matrix2[map(i-1, i, num_stops)] = matrix1[i-1]
        for j in range(i-2, -1, -1):
            prev_time = matrix2[map(j, i-1, num_stops)]
            for k in range(matrix1.shape[1]):
                if prev_time[k] == 0:
                    continue
                
                ind = int(k + matrix1[i-1][k]//10)
                assert ind < matrix1.shape[1]

                matrix2[map(j, i, num_stops), ind] = prev_time[k] + matrix1[i-1, ind]
                
    return matrix2


matrix1 = np.load("./assets/processed/matrix/bus_movements_2020_08-d-bus_movements_2020_08_05.db.npz")['matrix']

matrix2 = m1to2(matrix1, 534)

np.savez_compressed("./assets/processed/matrix2/bus_movements_2020_08-d-bus_movements_2020_08_05.db.npz", matrix = matrix2)