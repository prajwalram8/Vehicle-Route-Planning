# Import packages---------------------------------------------------------------------------------------------
## Data Acess and Manipulation
import pandas as pd
import numpy as np

## Geospatial Work
from shapely.geometry import shape, Point
# Geopandas
import geopandas
## Geospatial Work
import folium
from folium import plugins
import osmnx as ox
import networkx as nx
from shapely.geometry import shape, Point
from math import sin, cos, sqrt, atan2, radians

## Utilities
### importing necessary functions from dotenv library and loading variables from .env file
import os
import logging
from functools import partial
#from google.colab import userdata
from multiprocessing import cpu_count
from dotenv import load_dotenv 
load_dotenv()
# Notebook Configurations
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


from src.utils.data_loaders import save_dict, load_dict

# Functions---------------------------------------------------------------------------------------------

class DistanceCalculator:
    def __init__(self, bbox=None, network_type="drive"):
        self.G = None
        self.bbox = bbox
        self.network_type = network_type

    def create_graph(self):
        if self.bbox is None:
            raise ValueError("Bounding box is not set.")
        north, south, east, west = self.bbox
        self.G = ox.graph_from_bbox(north, south, east, west, network_type=self.network_type)
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)
        logger.info("Graph created")

    def calculate_duration(self, a, b, units='travel_time', duration=True):
        if self.G is None:
            self.create_graph()
        if a == b:
            return 0
        try:
            route = nx.shortest_path(self.G, source=a, target=b, method='dijkstra', weight=units)
            attrs = ox.utils_graph.route_to_gdf(self.G, route)
        except nx.NetworkXNoPath:
            return np.nan
        except Exception as e:
            logger.error(f"Error {e} occurred for inputs {a}, {b}")
            return np.nan

        return attrs[units].sum() if duration else attrs['length'].sum()
    

    @staticmethod
    def haversine_dist( x, y):
        # Approximate radius of earth in km
        R = 6373.0

        lat1 = radians(float(x[0]))
        lon1 = radians(float(x[-1]))
        lat2 = radians(float(y[0]))
        lon2 = radians(float(y[-1]))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        return distance

    @staticmethod
    def calculate_gd(args):
        x, y = args
        return DistanceCalculator.haversine_dist(x, y)

    def pairwise_distance(self, args, method='GD'):
        p1, p2 = args
        if method == 'GD':
            return self.calculate_gd((p1, p2))
        elif method == 'GRAPH':
            return self.calculate_duration(p1, p2)

    def df_to_dm(self, df, lat_col, long_col, uid, demand_ref, base_flag, method='GD'):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame")

        required_cols = [lat_col, long_col, uid, demand_ref, base_flag]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")

        xy_coordinates = list(map(lambda x: list(x), df[[lat_col, long_col]].values))
        xy_ids = df[uid].to_list()
        xy_demand = list(df[demand_ref].values.flatten())
        xy_demand[0] = 0

        max_workers = cpu_count()
        chunksize = 100  # Experiment with this value

        if method == 'GD':
            all_pairs = [(p1, p2) for p1 in xy_coordinates for p2 in xy_coordinates]
        elif method == 'GRAPH':
            if self.G is None:
                self.create_graph()
            xy_coordinates = list(map(lambda x: ox.distance.nearest_nodes(self.G, x[1], x[0]), xy_coordinates))
            all_pairs = [(p1, p2) for p1 in xy_coordinates for p2 in xy_coordinates]

        #with Executor(max_workers=max_workers) as executor:
        dm = list(map(partial(self.pairwise_distance, method=method), all_pairs))
        dm_matrix = np.array(dm).reshape(len(xy_coordinates), len(xy_coordinates))

        # Normalizing data for optumizer
        dm_matrix = dm_matrix*100
        dm_matrix = dm_matrix.astype(int)
        xy_demand = list(map(int, xy_demand))

        #logger.info(f"Average distance between the points: {dm_matrix.mean()}")
        #logger.info(f"Range distance between the points: {dm_matrix.min()} - {dm_matrix.max()}")

        return xy_ids, xy_coordinates, xy_demand, dm_matrix
    
    
def get_num_trucks(total_weight):
    # Calculate the ideal weights based on a 70-30 mix
    '''weight_3ton = 0.7 * total_weight
    weight_1ton = 0.3 * total_weight

    # Calculate the number of trucks, rounding to the nearest whole number
    num_3ton_trucks = round(weight_3ton / 3000)
    num_1ton_trucks = round(weight_1ton / 1000)

    # Calculate the total weight these trucks can carry
    total_carried_weight = (num_3ton_trucks * 3000) + (num_1ton_trucks * 1000)

    # Adjusting for the remainder if total carried weight is less than total weight
    while total_carried_weight < total_weight:
        # Check which addition gets closer to the goal
        if (total_weight - total_carried_weight) >= 3000:
            num_3ton_trucks += 1
            total_carried_weight += 3000
        else:
            num_1ton_trucks += 1
            total_carried_weight += 1000

    return [3000] * num_3ton_trucks + [1000] * num_1ton_trucks + [1000]*1'''

    #weight_3ton = 1.0 * total_weight
    #weight_1ton = 0.3 * total_weight

    # Calculate the number of trucks, rounding to the nearest whole number
    num_3ton_trucks = 22 #round(weight_3ton / 3000)
    #num_1ton_trucks = round(weight_1ton / 1000)

    # Calculate the total weight these trucks can carry
    total_carried_weight = (num_3ton_trucks * 3000) #+ (num_1ton_trucks * 1000)

    # Adjusting for the remainder if total carried weight is less than total weight
    while total_carried_weight < total_weight:
        # Check which addition gets closer to the goal
        if (total_weight - total_carried_weight) >= 3000:
            num_3ton_trucks += 1
            total_carried_weight += 3000
        else:
            num_1ton_trucks += 1
            total_carried_weight += 1000

    return [3000]*40 #[int((total_weight/num_3ton_trucks)+100)] * num_3ton_trucks #+ [1000] * num_1ton_trucks + [1000]*1

def create_data_model(demand, dm):
    """Stores the data for the problem."""
    data = {}
    vehicle_capacities = get_num_trucks(sum(demand))
    data["distance_matrix"] = dm
    data["demands"] = demand
    data["vehicle_capacities"] = vehicle_capacities
    data["num_vehicles"] = 40 #len(vehicle_capacities)
    data["depot"] = 0
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    routes_dict = {}
    #print(f"Objective: {solution.ObjectiveValue()}")
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data["num_vehicles"]):
        route_seq=[]
        route_seq_dict = {}
        index = routing.Start(vehicle_id)
        # plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        route_distance_list = []
        route_load = 0
        route_load_list = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data["demands"][node_index]
            # plan_output += f" {node_index} Load({route_load}) -> "
            route_seq.append(node_index)
            route_load_list.append(route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        # plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
        # plan_output += f"Distance of the route: {route_distance}m\n"
        # plan_output += f"Load of the route: {route_load}\n"
        # print(plan_output)
        total_distance += route_distance
        total_load += route_load
        route_seq_dict['route_plan'] = route_seq
        route_seq_dict['cumulative_route_load'] = route_load_list
        # route_seq_dict['route_distance'] = route_distance_list
        routes_dict[vehicle_id] =  route_seq_dict
    #print(f"Total distance of all routes: {total_distance}m")
    #print(f"Total load of all routes: {total_load}")
    return routes_dict


def run_model(data):
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]
    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Add node count constraint.
    def node_count_callback(from_index):
        """Returns 1 for each node to count the number of nodes visited."""
        return 1
    node_count_callback_index = routing.RegisterUnaryTransitCallback(node_count_callback)
    max_nodes_per_vehicle = 30
    routing.AddDimension(
        node_count_callback_index,
        5,  # no slack
        max_nodes_per_vehicle,
        True,  # start cumul to zero
        'NodeCount')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(30)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        #logger.info("Solution found!")
        output = print_solution(data, manager, routing, solution)
        #print("Solution found!")
    else:
        #logger.info("No solution found!")
        #print("No Solution found!")
        output = None
    
    # Save the Output
    save_location = r'assets\data\appData\model_output.json'  # Specify your file location
    save_dict(save_location, output)

    return manager, routing, solution, output













