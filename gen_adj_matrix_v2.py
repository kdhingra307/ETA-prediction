from utils import get_matrix1_map, get_route_details, get_mid_point, get_stops_details, haversine_dist
import numpy as np
from tqdm import tqdm

routes_data = get_route_details()
stops_data = get_stops_details()

nodes_map = get_matrix1_map(routes_data)

mid_points = [None]*nodes_map['size']

for e in nodes_map['map']:
    for k in nodes_map['map'][e]:
        mid_points[nodes_map['map'][e][k]] = (get_mid_point(*stops_data[e][:2], *stops_data[k][:2]))

adj_mx = np.full(fill_value=np.inf,shape=[nodes_map['size'], nodes_map['size']])


for route_id in tqdm(routes_data):
    each_route = routes_data[route_id]
    for stop_index in range(1, len(each_route)-1):
        prev_stop = each_route[stop_index-1]
        current_stop = each_route[stop_index]
        next_stop = each_route[stop_index+1]

        hop_start = nodes_map['map'][prev_stop][current_stop]
        hop_end = nodes_map['map'][current_stop][next_stop]

        adj_mx[hop_start, hop_start] = 0
        adj_mx[hop_end, hop_end] = 0
        adj_mx[hop_start, hop_end] = haversine_dist(*mid_points[hop_start], *mid_points[hop_end])




# ddss

# fail = []

# checks = 0
# for r1 in range(nodes_map['size']):
#     for r2 in range(nodes_map['size']):

#         if adj_mx[r1, r2] == np.inf:
#             continue
        
#         checks += 1
#         direct_compute = haversine_dist(*mid_points[r1], *mid_points[r2])
#         difference = direct_compute - adj_mx[r1, r2]
#         if difference > 0 or difference < -10000:
#             print(r1, r2, difference, direct_compute,  adj_mx[r1, r2])
#             fail.append(difference)


# print(len(fail), np.mean(fail), np.std(fail), checks)


distances = adj_mx[~np.isinf(adj_mx)].flatten()
std = distances.std()
#print(std)
adj_mx = np.exp(-np.square(adj_mx / std))
print(np.mean(adj_mx), np.min(adj_mx), np.max(adj_mx))
# Make the adjacent matrix symmetric by taking the max.
# adj_mx = np.maximum.reduce([adj_mx, adj_mx.T])

# Sets entries that lower than a threshold, i.e., k, to zero for sparsity.
adj_mx[adj_mx < 0.01] = 0

np.savez_compressed("./adj_matrix", adj_mx)
