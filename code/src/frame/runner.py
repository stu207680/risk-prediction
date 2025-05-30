from VCRA_init import model_builder

from algorithms.ARSC_FC.utils.calculations.functions import inputs_function, costs_function_single_edge_static, is_dominated_function

from sklearn.neighbors import BallTree

import state_storage

import IO.file_manager
import IO.visualization_manager

import algorithms.ARSC_FC.utils.IO.file_manager
import algorithms.ARSC_FC.utils.IO.visualization_manager

import algorithms.ARSC_FC.ARSC

import math
import numpy as np
import os.path
import pandas as pd
# import pyarrow as pa
# import pyarrow.parquet as pq

# main entry point of this runner!
if __name__ == "__main__":
  # hidden short-hand function to ensure an unique object instantiation.
  def create_nodes(storage, dataframe, ball_tree, graph):
    # hidden short-hand function to map a node to the nearest data entry.
    def find_nearest_node(graph, coordinates):
      minimum = math.inf, None
      for node in list(graph.nodes()):
        distance = abs(node.coordinates[0] - coordinates[0]) + abs(node.coordinates[1] - coordinates[1])
        if minimum[0] > distance:
          minimum = distance, node
      return minimum[1]

    source_node = find_nearest_node(graph = graph, coordinates = storage.dot_config["algorithm_parameter(s)"]["source_node"])
    inputs_function(storage = storage, data = dataframe, ball_tree = ball_tree, node = source_node)
    destination_node = find_nearest_node(graph = graph, coordinates = storage.dot_config["algorithm_parameter(s)"]["destination_node"])
    inputs_function(storage = storage, data = dataframe, ball_tree = ball_tree, node = destination_node)
    return source_node, destination_node

  # interpolates speed deltas between the minimum and maximum speed with k as stepssize
  def generate_speeds_function(min, max, k):
    return np.arange(max - (max - min) / (k + 1.0), min, -((max - min) / (k + 1.0)))

  # initialize the storage and read the configuration
  storage = state_storage.STATE_STORAGE()
  storage.path_root_code = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
  storage.raw_file_path = f"{storage.path_root_code}/.config/ARSC/ARSC.config"
  storage = IO.file_manager.FILE_MANAGER().read_dot_config(storage = storage)[1]
  storage.file_name = "ARSC"
  storage.results = {storage.dot_config["algorithm_name"]: []}

  # build the model
  if os.path.exists("source_code/risk-prediction/code/data/.ML_model/ARSC_ML_model [0001].ML_model") and os.path.isfile("source_code/risk-prediction/code/data/.ML_model/ARSC_ML_model [0001].ML_model"):
    storage.dot_config["data"]["ML_model"] = "source_code/risk-prediction/code/data/.ML_model/ARSC_ML_model [0001].ML_model"
  else:
    geoDataframe = model_builder(file_paths = storage.dot_config["data"]["file_paths"])
    pd.to_pickle(geoDataframe, "source_code/risk-prediction/code/data/.ML_model/geoDataframe.pickle")
  storage.dot_config["data"]["ML_data"] = "source_code/risk-prediction/code/data/.ML_model/geoDataframe.pickle"
  geoDataframe = pd.read_pickle("source_code/risk-prediction/code/data/.ML_model/geoDataframe.pickle")
  ball_tree = BallTree(data = np.deg2rad(geoDataframe.geometry.get_coordinates())[["y", "x"]], leaf_size = 40, metric = "haversine")

  # build the graph and set the algorithm parameters
  graph, _, _ = IO.file_manager.FILE_MANAGER().create_graph(create_function = algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().create_H3_saronic_golf_graph, storage = storage, dataframe = geoDataframe)[1]
  source_node, destination_node = create_nodes(storage = storage, dataframe = geoDataframe, ball_tree = ball_tree, graph = graph)
  start_date = storage.dot_config["algorithm_parameter(s)"]["start_date"]
  k = storage.dot_config["algorithm_parameter(s)"]["k"]
  speed_interval = storage.dot_config["algorithm_parameter(s)"]["speed_interval"]

  # execute the algorithm
  _, skyline_routes, _ = algorithms.ARSC_FC.ARSC.ALGORITHM_ARSC().execute_algorithm(argument_vector = [storage, costs_function_single_edge_static, is_dominated_function, None, (graph, source_node, destination_node), start_date, generate_speeds_function(min = speed_interval[0], max = speed_interval[1], k = k), geoDataframe, ball_tree])[1]
  storage.results[storage.dot_config["algorithm_name"]].append((_, skyline_routes))

  # save the results and transform them into a parquet file
  IO.visualization_manager.VISUALIZATION_MANAGER().write_to_(write_function = algorithms.ARSC_FC.utils.IO.visualization_manager.VISUALIZATION_MANAGER().write_to_csv, storage = storage)
  # pq.write_table(pa.Table.from_pandas(pd.read_csv(f"{storage.path_root_code}/data/.result/.csv/{storage.file_name}_RF [{1:04d}].csv")), f"{storage.path_root_code}/data/.result/.parquet/{storage.file_name}_RF [{1:04d}].parquet")