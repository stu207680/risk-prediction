from algorithms.ARSC_FC.utils.calculations.functions import clean_function

from algorithms.ARSC_FC.utils.calculations.CRI_HLP import homogenize_units
from algorithms.ARSC_FC.utils.calculations.ENC import encountering_vessels

import algorithms.utils.meta_structures.algorithm_abstract

import algorithms.ARSC_FC.utils.IO.file_manager

import algorithms.ARSC_FC.utils.data_structures.ML_model
import algorithms.ARSC_FC.utils.data_structures.embedding
import algorithms.ARSC_FC.utils.data_structures.node
import algorithms.ARSC_FC.utils.data_structures.path

import math
import os.path
import pandas as pd
import queue

"""
purpose: Class that provides the Advanced Route Skyline Computation (ARSC) algorithm.\n
"""
class ALGORITHM_ARSC(algorithms.utils.meta_structures.algorithm_abstract.ALGORITHM_ABSTRACT):
  """
  purpose: Determines route skyline(s) for a multi-preference path using the Advanced Route Skyline Computation (ARSC) algorithm.\n
  I/O:
    - input: @storage stores the @embedding and @AS_dimension.
             @costs_function determines the current cost(s) of a (sub-)route.
             @is_function determines when a (sub-)route is Pareto-optimal.
             @embedding contains the Lipschitz embedding.
             @graph represents the NetworkX graph within the nodes are stored.
             @source_node represents the source node of the route (begin of the skyline).
             @destination_node represents the destination node of the route (end of the skyline).
             @start_date represents the time at which the route search starts at source_node.
             @speeds represents the speeds.
             @dataframe contains the data (optional).
             @ball_tree represents the index structure for the nearest neighbor queries (optional).
    - output: Returns either the Lipschitz embedding with route skyline(s) or an error message.
  """
  def ARSC(self, storage, costs_function, is_dominated_function, embedding, graph, source_node, destination_node, start_date, speeds, dataframe = None, ball_tree = None):

    MACRO_OVERALL_PATHS = 0
    MACRO_PRUNED_PATHS = 0

    MACRO_SPEEDS = speeds

    # hidden short-hand function to map an node to the nearest data entry.
    def find_nearest_node(graph, coordinates):
      minimum = math.inf, None
      for node in list(graph.nodes()):
        distance = abs(node.coordinates[0] - coordinates[0]) + abs(node.coordinates[1] - coordinates[1])
        if minimum[0] > distance:
          minimum = distance, node
      return minimum[1]

    # hidden short-hand function to expand the given sub-route with one hop in each direction.
    def expand_route(storage, sub_route, dataframe, ball_tree, MACRO_OVERALL_PATHS):
      # hidden short-hand function to determine the next possible speed.
      def in_range(sub_route, speed):
        if len(sub_route.speeds_history) == 0:
          return True
        if sub_route.speeds_history[-1] == min(MACRO_SPEEDS):
          if speed > sub_route.speeds_history[-1] + storage.dot_config["algorithm_parameter(s)"]["speed_delta"]:
            return False
        if sub_route.speeds_history[-1] == max(MACRO_SPEEDS):
          if speed < sub_route.speeds_history[-1] - storage.dot_config["algorithm_parameter(s)"]["speed_delta"]:
            return False
        if speed < sub_route.speeds_history[-1] - storage.dot_config["algorithm_parameter(s)"]["speed_delta"] or speed > sub_route.speeds_history[-1] + storage.dot_config["algorithm_parameter(s)"]["speed_delta"]:
          return False
        return True

      adjacent_edges = graph.edges(sub_route.destination_node, data = True)
      expanded_routes = []
      for edge in adjacent_edges:
        for speed in MACRO_SPEEDS:
          if not in_range(sub_route = sub_route, speed = speed):
            continue
          costs_delta = costs_function(storage = storage, edge = edge, time = sub_route.timestamp_history[-1], speed = speed, dataframe = dataframe, ball_tree = ball_tree)
          if costs_delta[1] >= storage.dot_config["algorithm_parameter(s)"]["cut_off"]:
            continue
          expanded_route = algorithms.ARSC_FC.utils.data_structures.path.PATH(source_node = sub_route.source_node, destination_node = edge[1], costs_vector = sub_route.costs_vector.copy())
          expanded_route.update_intermediate_nodes(intermediate_nodes = sub_route.intermediate_nodes)
          expanded_route.update_timestamp_history(timestamp_history = sub_route.timestamp_history + [sub_route.timestamp_history[-1] + pd.Timedelta(hours = costs_delta[0])])
          expanded_route.costs_vector[0] = sum([sub_route.costs_vector[0], costs_delta[0]])
          expanded_route.costs_vector[1] = max([sub_route.costs_vector[1], costs_delta[1]])
          expanded_route.costs_vector_history = sub_route.costs_vector_history + [costs_delta]
          expanded_route.speeds_history = sub_route.speeds_history + [speed]
          expanded_routes.append(expanded_route)
      return expanded_routes, MACRO_OVERALL_PATHS + len(expanded_routes)

    # checks which machine learning model configuration should be used:
    if storage.dot_config["data"]["ML_model"]:
      if not (os.path.exists(storage.dot_config["data"]["ML_model"]) and os.path.isfile(storage.dot_config["data"]["ML_model"])):
        return "@error: model:model-file not found!", None
      storage.dot_config["data"]["ML_data"] = pd.read_pickle(storage.dot_config["data"]["ML_data"])
      storage.dot_config["data"]["ML_model"] = algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().load_ML_model(storage = storage)[1]
    else:
      if not dataframe is None:
        storage.dot_config["data"]["ML_data"] = dataframe
      elif storage.dot_config["data"]["ML_data"]:
        if not (os.path.exists(storage.dot_config["data"]["ML_data"]) and os.path.isfile(storage.dot_config["data"]["ML_data"])):
          return "@error: model:data-file not found!", None
        storage.dot_config["data"]["ML_data"] = pd.read_pickle(storage.dot_config["data"]["ML_data"])
      else:
        return "@error: model:data-file not found!", None
      encountering_pairs, results = encountering_vessels(data = storage.dot_config["data"]["ML_data"], dt_name = "datetime")
      file_ID = len(storage.results[storage.dot_config["algorithm_name"]])
      encountering_pairs.to_pickle(f"source_code/risk-prediction/code/data/.ML_model/{storage.file_name}_encountering_pairs [{file_ID + 1:04d}].pickle")
      results = homogenize_units(results)
      results.to_pickle(f"source_code/risk-prediction/code/data/.ML_model/{storage.file_name}_results [{file_ID + 1:04d}].pickle")
      ML_model = algorithms.ARSC_FC.utils.data_structures.ML_model.ML_MODEL().create_ML_model(storage = storage, ML_data = results)
      storage.dot_config["data"]["ML_model"] = ML_model
      algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().save_ML_model(storage = storage, ML_model = ML_model)
    # checks which Lipschitz embedding configuration should be used:
    if storage.dot_config["data"]["embedding"]:
      if not (os.path.exists(storage.dot_config["data"]["embedding"]) and os.path.isfile(storage.dot_config["data"]["embedding"])):
        return "@error: embedding-file not found!", None
      embedding, graph = algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().load_embedding(storage = storage)
      source_node = find_nearest_node(graph = graph, coordinates = source_node.coordinates)
      destination_node = find_nearest_node(graph = graph, coordinates = destination_node.coordinates)
    elif not embedding:
      embedding = algorithms.ARSC_FC.utils.data_structures.embedding.EMBEDDING().create_embedding(storage = storage, graph = graph)
      algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().save_embedding(storage = storage, embedding = embedding, graph = graph)
    storage.dot_config["algorithm_parameter(s)"]["speed"] = max(speeds)

    import time
    start_time = time.time()

    priority_queue = queue.PriorityQueue()
    skyline_routes = []
    initial_route = algorithms.ARSC_FC.utils.data_structures.path.PATH(source_node = source_node, destination_node = source_node, costs_vector = [0.0 for _ in range(storage.dot_config["algorithm_parameter(s)"]["AS_dimension"])])
    initial_route.update_timestamp_history(timestamp_history = [pd.Timestamp(start_date)])
    initial_route.costs_vector_history = [(0.0, 0.0)]
    initial_route.speeds_history = []
    source_node.update_sub_route_skyline(sub_route = initial_route)
    MACRO_OVERALL_PATHS += 1
    priority_queue.put((0, source_node))
    while not (source_node == destination_node or priority_queue.empty()):
      _, v_i = priority_queue.get()
      sub_route_index = 0
      while sub_route_index < len(v_i.sub_route_skyline):
        sub_route = v_i.sub_route_skyline[sub_route_index]
        if skyline_routes:
          # determines the lower bound for the current sub-route
          if not sub_route.attributes_vector:
            sub_route.calculate_attributes_vector(embedding = embedding, destination_node = destination_node)
          mock_route = algorithms.ARSC_FC.utils.data_structures.path.PATH(source_node = sub_route.source_node, destination_node = sub_route.destination_node, costs_vector = sub_route.attributes_vector)
          if not is_dominated_function(sub_route = mock_route, routes = skyline_routes):
            del v_i.sub_route_skyline[sub_route_index]
            MACRO_PRUNED_PATHS += 1
            continue
        if sub_route.processed:
          sub_route_index += 1
          continue
        # expands the current sub-route with one hop in each direction
        expanded_sub_routes, MACRO_OVERALL_PATHS = expand_route(storage = storage, sub_route = sub_route, dataframe = dataframe, ball_tree = ball_tree, MACRO_OVERALL_PATHS = MACRO_OVERALL_PATHS)
        for expanded_sub_route in expanded_sub_routes:
          # checks if the destination is reached and the new found skyline not already dominated:
          if expanded_sub_route.destination_node == destination_node:
            if is_dominated_function(sub_route = expanded_sub_route, routes = skyline_routes):
              MACRO_PRUNED_PATHS = clean_function(sub_route = expanded_sub_route, routes = skyline_routes, MACRO_PRUNED_PATHS = MACRO_PRUNED_PATHS)
              skyline_routes = sorted(skyline_routes + [expanded_sub_route], key = lambda x: x.costs_vector[0], reverse = True)
          else:
            v_next = expanded_sub_route.destination_node
            # prunes based on the second sub-route skyline criterion
            if is_dominated_function(sub_route = expanded_sub_route, routes = v_next.sub_route_skyline):
              MACRO_PRUNED_PATHS = clean_function(sub_route = expanded_sub_route, routes = v_next.sub_route_skyline, MACRO_PRUNED_PATHS = MACRO_PRUNED_PATHS)
              expanded_sub_route.calculate_attributes_vector(embedding = embedding, destination_node = destination_node)
              v_next.sub_route_skyline.append(expanded_sub_route)
              priority_queue.put((v_next.min_score(), v_next))
        sub_route.processed = True
        sub_route_index += 1

    end_time = time.time()

    return "@error: no error!", (embedding, skyline_routes, (MACRO_OVERALL_PATHS, MACRO_PRUNED_PATHS, end_time - start_time))

  """
  purpose: Execute the Advanced Route Skyline Computation (ARSC) algorithm.\n
  I/O:
    - input: @argument_vector represents the argument vector containing all necessary information to execute the algorithm.
    - output: Returns either the Lipschitz embedding with route skyline(s) or an error message.
  """
  def execute_algorithm(self, argument_vector):
    # checks if the source and destination node are part of the graph:
    if not (argument_vector[4][1] in argument_vector[4][0].nodes() and argument_vector[4][2] in argument_vector[4][0].nodes()):
      return "@error: source and/or destination not found in the graph!", None
    return self.ARSC(storage = argument_vector[0],
                     costs_function = argument_vector[1],
                     is_dominated_function = argument_vector[2],
                     embedding = argument_vector[3],
                     graph = argument_vector[4][0],
                     source_node = argument_vector[4][1],
                     destination_node = argument_vector[4][2],
                     start_date = argument_vector[5],
                     speeds = argument_vector[6],
                     dataframe = argument_vector[7],
                     ball_tree = argument_vector[8])