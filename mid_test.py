import utils
import numpy as np

stops = utils.get_stops_details()
def check():
    choice = np.random.choice(list(stops.keys()))
    rand_stop1 = stops[choice][:2]
    choice = np.random.choice(list(stops.keys()))
    rand_stop2 = stops[choice][:2]

    mid_point = utils.get_mid_point(*rand_stop1, *rand_stop2)
    dist1 = utils.haversine_dist(*mid_point, *rand_stop2)
    dist2 = utils.haversine_dist(*mid_point, *rand_stop1)
    
    return (dist1, dist2, choice)

print(check())