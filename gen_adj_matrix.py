from utils import get_matrix1_map, get_route_details, get_mid_point, get_stops_details, haversine_dist
import numpy as np
from tqdm.notebook import tqdm

routes_data = get_route_details()
stops_data = get_stops_details()

nodes_map = get_matrix1_map(routes_data)

mid_points = [None]*nodes_map['size']

for e in nodes_map['map']:
    for k in nodes_map['map'][e]:
        mid_points[nodes_map['map'][e][k]] = (get_mid_point(*stops_data[e][:2], *stops_data[k][:2]))

adj_mx = np.full(fill_value=np.inf,shape=[nodes_map['size'], nodes_map['size']])

def fill_recursive(stop_list, e):

    if e == len(stop_list) - 1:
        return [], [], stop_list[e], None
    else:
        nodes_next, distance_dp,  k, s = fill_recursive(stop_list, e+1)
        p = nodes_map['map'][stop_list[e]][k]

        if s is not None:
            new_dist = haversine_dist(*mid_points[p], *mid_points[s])
        
        
        for i in range(len(nodes_next)):
            distance_dp[i] += new_dist
            adj_mx[p][nodes_next[i]] = min(distance_dp[i], adj_mx[p][nodes_next[i]])
        
        distance_dp.append(0)
        nodes_next.append(p)
        adj_mx[p, p] = 0

        return nodes_next, distance_dp, stop_list[e], p


for i in tqdm(routes_data):
    fill_recursive(routes_data[i], 0)


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
