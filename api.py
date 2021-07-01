# %%
import json
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


from flask import Flask, request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
import metrics



@app.route("/initialize")
def initialize():

    route_id = int(request.args['route_id'])
    start_stop = int(request.args['start_stop'])
    n_hops = int(request.args['n_hops'])

    return metrics.initialize(start_stop, n_hops, route_id=route_id)