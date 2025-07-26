from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import json
import time
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

app = Flask(__name__)
socketio = SocketIO(app)

with open('bins_data.json') as f:
    bins_data = json.load(f)

last_alert_times = {}

ALERT_THRESHOLD = 80
COOLDOWN = 5 * 60 * 60

def check_and_alert(bin_data):
    bin_id = bin_data['bin_id']
    fill_level = bin_data['fill_level']
    current_time = time.time()

    last_alert = last_alert_times.get(bin_id, 0)
    if fill_level >= ALERT_THRESHOLD and (current_time - last_alert) > COOLDOWN:
        alert_msg = f"⚠️ ALERT: Bin {bin_id} is nearly full at {fill_level}%!"
        last_alert_times[bin_id] = current_time
        socketio.emit('alert', {'message': alert_msg})
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html', bins=bins_data)

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    data = request.json
    bin_id = data['bin_id']
    bins_data[bin_id] = data
    check_and_alert(data)
    return jsonify({'status': 'success'})

@app.route('/generate-route')
def generate_route():
    full_bins = [b for b in bins_data.values() if b['fill_level'] >= ALERT_THRESHOLD]

    if not full_bins:
        return jsonify({'route': [], 'message': 'No bins need collection'})

    locations = [b['location'] for b in full_bins]

    def compute_distance_matrix(locations):
        distances = {}
        for i, loc_i in enumerate(locations):
            distances[i] = {}
            for j, loc_j in enumerate(locations):
                if i == j:
                    distances[i][j] = 0
                else:
                    distances[i][j] = int(((loc_i[0] - loc_j[0])**2 + (loc_i[1] - loc_j[1])**2)**0.5 * 100000)
        return distances

    distance_matrix = compute_distance_matrix(locations)

    manager = pywrapcp.RoutingIndexManager(len(locations), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    route_order = []
    if solution:
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route_order.append(full_bins[node]['bin_id'])
            index = solution.Value(routing.NextVar(index))

    return jsonify({'route': route_order})

if __name__ == '__main__':
    socketio.run(app, debug=True)
