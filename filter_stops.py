#%%
from tqdm import tqdm
import numpy as np
import folium
import utils

#%%
utils.version="1.2"
haversine_dist = utils.haversine_dist
stop_data = utils.get_stops_details()

delhi_coordinates = [28.664666, 77.230633]

#%%
def plot_route(route_id, error_stops):
    routes = route_data[route_id]
    fmap= folium.Map(
        location=stop_data[routes[0]][:2], 
        zoom_start=13)
    
    _id = 0
    for each_route in routes:
        if _id in error_stops:
            icon = folium.map.Icon(color="red")
        else:
            icon = folium.map.Icon(color="blue")


        folium.Marker(
            location=stop_data[each_route][:2],
            popup="stuff_{}_{}_{}".format(_id, stop_data[each_route][3], each_route),
            icon=icon
            
        ).add_to(fmap)
        _id += 1
    
    prev = stop_data[routes[0]][:2]
    for each_route in routes:
        each_route = stop_data[each_route][:2]
        folium.vector_layers.PolyLine([prev, each_route]).add_to(fmap)
        prev = each_route
    
    return fmap

#%%
def iterate_over_routes(stop_data, route_data):
    contents = []
    for each_route_id in tqdm(route_data):
        each_route = route_data[each_route_id]
        for cur_id in range(1, len(each_route)-1):
            prev_stop = stop_data[each_route[cur_id-1]][:2]
            cur_stop = stop_data[each_route[cur_id]][:2]
            next_stop = stop_data[each_route[cur_id+1]][:2] 
            distance_centre = utils.haversine_dist(*delhi_coordinates, *cur_stop)
            L1 = utils.haversine_dist(*prev_stop, *cur_stop)
            L2 = utils.haversine_dist(*cur_stop, *next_stop)
            L3 = utils.haversine_dist(*prev_stop, *next_stop)
            contents.append({
                "route_id": each_route_id,
                "r": (L1+L2)/L3,
                "L1": L1,
                "L2": L2,
                "L3": L3,
                "stop_index": cur_id,
                "stop_id": each_route[cur_id],
                "centre_d": distance_centre})

    return contents

#%%
def clean_route_data(failed):    
    for each_entry in failed:
        route_data[each_entry[0]][each_entry[5]] = "-1"
    
    for each_route in route_data:
        route_data[each_route] = route_data[each_route][route_data[each_route]!="-1"]
    
    print(route_data[each_route][route_data[each_route]!="-1"].shape)
#%%


def first_check(contents):
    passed = []
    failed = []
    for each_content in tqdm(contents):
        if each_content[-1] > 100*1000:
            failed.append(each_content)
        else:
            passed.append(each_content)

    return passed, failed

#%%
def second_check(contents):
    passed = []
    failed = []
    for each_entry in tqdm(contents):
        if each_entry[1] > 20:
            failed.append(each_entry)
        else:
            passed.append(each_entry)
    
    return passed, failed
#%%
route_data = utils.get_route_details()
contents = iterate_over_routes(stop_data, route_data)
#%%
passed, failed = first_check(contents)
#%%
clean_route_data(failed)
contents = iterate_over_routes(stop_data, route_data)
#%%
passed, failed = second_check(contents)
failed = sorted(failed, key=lambda e:-1*e[1])
failed = np.array(failed)

# %%



rogue_route = [
    ['1365', ["temp_1418", "temp_197"]],
    ['1515', ['641' 'temp_2647' 'temp_3397']],
]

#%%
def get_same_stops(failed):
    similar_stops = []
    for index in range(len(failed)):
        similar_stops.append(np.concatenate([[int(failed[index][0])], 
        route_data[int(failed[index][0])][np.array([int(failed[index][5])-1,int(failed[index][5])+1])]]))
    return np.array(similar_stops)
# %%

def save_csv(array, name):
    np.savetxt(name, array, delimiter=",", fmt="%s")

# %%

def details(failed, index):
    print(failed[index])
    print(route_data[int(failed[index][0])][int(failed[index][5])-1:int(failed[index][5])+2])
    for e in route_data[int(failed[index][0])][int(failed[index][5])-1:int(failed[index][5])+2]:

    print()
    return plot_route(int(failed[index][0]), [int(failed[index][5])-1, int(failed[index][5]), int(failed[index][5])+1])


# %%
