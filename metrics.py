# %%
from datetime import datetime
from tqdm import tqdm
from matplotlib import pyplot as plt
from utils import get_stops_details, haversine_dist
from read_from_file import get_start_stops, get_time_tree, location
import numpy as np


stop_data = get_stops_details()
matrix = np.load(
    "./assets/processed/matrix2/matrix2_august_September.npz")['matrix']
time_tree = get_time_tree()

#%%
def initialize():

    start_stop, current_time, trip_ids = get_start_stops(time_tree)

    m1 = matrix[matrix[:, 1] == int(start_stop)]
    m1 = m1[:, np.array([0, 2, current_time.hour+3])]

    for each_trip in trip_ids:
        each_trip.append(m1[m1[:, 0] == int(each_trip[0])])


    return trip_ids, current_time



#%%
trip_ids, current_time = initialize()

#%%
for each_trip in trip_ids:
    each_trip[-1][:, -1] += 0.5*np.arange(len(each_trip[-1][:, -1]))

#%%
hops = np.zeros(100)
count = np.zeros(100)
time_stamp = current_time.timestamp()
coordinates1 = []
coordinates2 = []
for each_trip in trip_ids[1:2]:
    i = 0
    for each_hop in each_trip[-1]:
        gt_coord = stop_data[str(int(each_hop[1]))][:2]
        pred_coord = location(time_tree, int(time_stamp + 60*each_hop[-1]), each_trip[0], each_trip[1])
        coordinates1.append(gt_coord)
        coordinates2.append(pred_coord)
        if pred_coord[0] != -1:
            hops[i]+=(haversine_dist(*gt_coord, *pred_coord[1:]))
            count[i] += 1
        i+=1
        # count[i]+=1

print(hops[count!=0]/count[count!=0])
    




# %%
from read_from_file import start_time
def location(timetree, time, route_id, trip_id):
    time_lag = int((time - start_time.timestamp())/10)
    try:
        trip_data = timetree[time_lag][route_id][trip_id]
    except Exception as e:
        try:
            trip_data  = timetree[time_lag+1][route_id][trip_id]
        except:
            try:
                 trip_data  = timetree[time_lag-1][route_id][trip_id]
            except:
                return [-1]
    return trip_data[0]
# %%


import folium
def plot(c1, c2):

    fmap= folium.Map(
        location=list(c1[0]), 
        zoom_start=13)

    _id = 0
    for e in c1:
        icon = folium.map.Icon(color="red", icon="home")
        folium.Marker(location=list([float(e[0]), float(e[1])]), icon=icon, popup = "{}".format(_id)).add_to(fmap)
        _id += 1
    
    _id = 0
    for e in c2:
        icon = folium.map.Icon(color="green", icon="adjust")
        if len(e) == 1:
            continue
        if len(e) == 3:
            e = e[1:]
        folium.Marker(location=e, icon=icon, popup = "{}".format(_id)).add_to(fmap)
        _id += 1

    fmap.save("stuff.html")
    return fmap
    
# %%
