from algorithms.ARSC_FC.utils.calculations.functions import inputs_function, costs_function_single_edge_static, is_dominated_function

from colour import Color
from random import sample
from sklearn.neighbors import BallTree

import algorithms.utils
import state_storage

import IO.file_manager
import IO.visualization_manager

import algorithms.ARSC_FC.utils.data_structures.node
import algorithms.ARSC_FC.utils.data_structures.ML_model
import algorithms.ARSC_FC.utils.data_structures.path

import algorithms.ARSC_FC.ARSC

import algorithms.ARSC_FC.utils.IO.file_manager
import algorithms.ARSC_FC.utils.IO.visualization_manager

import builtins
import cProfile
import folium
import math
import numpy as np
import os.path
import pandas as pd
import pstats
import queue

MACRO_MULTIPLE_RUNS = False
MACRO_H3_RESOLUTION = [8, 9, 10, 11, 12, 13, 14, 15]
MACRO_RADIUS = [1850.0 / 16, 1850.0 / 8, 1850.0 / 4, 1850.0 / 2, 1850.0]
MACRO_FORCE_CREATE_GRAPH = False
MACRO_SAVE_GRAPH = MACRO_FORCE_CREATE_GRAPH

MACRO_ITERATIONS = 20
MACRO_CUT_OFF = [0.251, 0.501, 0.751, 1.01]

MACRO_TIMESTAMPS = ["2017-08-01 00:00:00", "2017-08-01 6:00:00", "2017-08-01 12:00:00", "2017-08-01 18:00:00"]
MACRO_SPEEDS = [8.0, 14.0]
MACRO_K = [8]

MACRO_CREATE_SKYLINE_ROUTES = True
MACRO_SAVE_SKYLINE_ROUTES = True
MACRO_LOAD_SKYLINE_ROUTES = False
MACRO_PARSE_SKYLINE_ROUTES = False

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
    
# hidden short-hand function to generate speeds.
def generate_speeds_function(min, max, k):
  return np.arange(max - (max - min) / (k + 1.0), min, -((max - min) / (k + 1.0)))

# hidden short-hand function to calculate the shortest path between two nodes.
def Dijkstra(graph, source_node, destination_node, start_date, speeds, cut_off):
  import time
  start_time = time.time()

  dijkstra = dict()
  priority_queue = queue.PriorityQueue()

  start_date = pd.Timestamp(start_date)
  shortest_path = math.inf
  priority_queue.put((0.0, (source_node, start_date)))
  while not priority_queue.empty():
    path_cost, (u_node, timestamp) = priority_queue.get()
    if not u_node.ID in dijkstra:
      dijkstra[u_node.ID] = (math.inf, start_date)
    elif not dijkstra[u_node.ID][0] == math.inf:
      continue
    dijkstra[u_node.ID] = (path_cost, timestamp)
    if u_node.ID == destination_node.ID:
      shortest_path = path_cost
      break
    for edge in graph.edges(u_node, data = True):
      v_node = edge[1]
      if v_node.ID in dijkstra and not dijkstra[v_node.ID][0] == math.inf:
        continue
      buffer = []
      for speed in speeds:
        time_delta, cri = costs_function_single_edge_static(storage = storage, edge = edge, time = timestamp, speed = speed)
        if cri < cut_off:
          buffer.append(time_delta)
      if not buffer:
        continue
      shortest_path = min(buffer)
      if shortest_path != math.inf:
        priority_queue.put((path_cost + shortest_path, (v_node, timestamp + pd.Timedelta(hours = shortest_path))))

  end_time = time.time()

  return shortest_path, end_time - start_time

# hidden short-hand function to visualize result(s).
def visualize(storage, file_name, source_node, destination_node, mode = "obstacles", coloring = "RCI_grading", args = {"left_border": Color("#084081"), "right_border": Color("#f7fcf0"), "cri_threshold": 0.75}):
  # hidden short-hand function to find alternative routes.
  def find_alternatives(alternatives, position, time, cri, min_deviation = 0):
    buffer = []
    for route in alternatives:
      if position + 1 >= len(route.intermediate_nodes):
        continue
      u, v = route.intermediate_nodes[position:position + 2]
      _, own_cri = costs_function_single_edge_static(storage = storage, edge = (u, v), time = time, speed = route.speeds_history[position], visualize = False)
      if cri > own_cri + min_deviation:
        buffer.append((u, v))
    return buffer

  map = folium.Map(location = source_node.coordinates, tiles = "OpenStreetMap", zoom_start = 12)
  map.add_child(folium.Marker(location = source_node.coordinates, icon = folium.Icon(color = "black")))
  map.add_child(folium.Marker(location = destination_node.coordinates, icon = folium.Icon(color = "black")))
  if mode == "no_obstacles":
    RCI_grading_colors = list(args["left_border"].range_to(args["right_border"], len(storage.results[storage.dot_config["algorithm_name"]][0][1])))
    no_RCI_grading_colors = ["blue", "brown", "cyan", "gray", "green", "olive", "orange", "pink", "purple", "red"]

    routes = storage.results[storage.dot_config["algorithm_name"]][0][1]
    if coloring == "RCI_grading":
      routes = sorted(storage.results[storage.dot_config["algorithm_name"]][0][1], key = lambda x: x.costs_vector[1], reverse = True)
    for index, route in enumerate(routes):
      if coloring == "RCI_grading":
        color = RCI_grading_colors[index].hex
      elif coloring == "no_RCI_grading":
        color = no_RCI_grading_colors[index % len(no_RCI_grading_colors)]
      else:
        raise ValueError("@visualize: coloring invalid value!")
      map.add_child(folium.PolyLine([node.coordinates for node in route.intermediate_nodes], color = color))
  elif mode == "obstacles":
    if coloring == "RCI_grading":
      for index, route in enumerate(storage.results[storage.dot_config["algorithm_name"]][0][1]):
        RCI_grading_colors = list(args["right_border"].range_to(args["left_border"], len(list(dict.fromkeys([rci for _, rci in route.costs_vector_history])))))

        sindex = 0
        while sindex < len(route.intermediate_nodes) - 1:
          map.add_child(folium.PolyLine([route.intermediate_nodes[sindex].coordinates, route.intermediate_nodes[sindex + 1].coordinates], color = RCI_grading_colors[sum(_rci < route.costs_vector_history[sindex][1] for _rci in list(dict.fromkeys([rci for _, rci in route.costs_vector_history])))].hex))
          sindex += 1
    elif coloring == "no_RCI_grading":
      RCI_grading_colors = list(args["left_border"].range_to(args["right_border"], max(builtins.map(lambda route: len(route.intermediate_nodes), storage.results[storage.dot_config["algorithm_name"]][0][1]))))

      index = 0
      sindex = 0
      max_iterations = max([len(route.intermediate_nodes) for route in storage.results[storage.dot_config["algorithm_name"]][0][1]])
      while True:
        route = storage.results[storage.dot_config["algorithm_name"]][0][1][index]
        if index + 1 >= len(storage.results[storage.dot_config["algorithm_name"]][0][1]):
          index = 0
          sindex += 1
        else:
          index += 1
        if sindex >= len(route.intermediate_nodes) - 1:
          if sindex >= max_iterations:
            break
          continue
        u, v = route.intermediate_nodes[sindex:sindex + 2]
        map.add_child(folium.PolyLine([u.coordinates, v.coordinates], color = RCI_grading_colors[sindex].hex))
        _, _, nearest_neighbors = costs_function_single_edge_static(storage = storage, edge = (u, v), time = route.timestamp_history[sindex], speed = route.speeds_history[sindex], visualize = True)
        for nearest_neighbor in nearest_neighbors:
          map.add_child(folium.CircleMarker([nearest_neighbor.lat, nearest_neighbor.lon], radius = 2, color = RCI_grading_colors[sindex].hex))
    elif coloring == "partial_RCI_grading":
      index = 0
      sindex = 0
      max_iterations = max([len(route.intermediate_nodes) for route in storage.results[storage.dot_config["algorithm_name"]][0][1]])
      while True:
        route = storage.results[storage.dot_config["algorithm_name"]][0][1][index]
        if index + 1 >= len(storage.results[storage.dot_config["algorithm_name"]][0][1]):
          index = 0
          sindex += 1
        else:
          index += 1
        if sindex >= len(route.intermediate_nodes) - 1:
          if sindex >= max_iterations:
            break
          continue
        u, v = route.intermediate_nodes[sindex:sindex + 2]
        _, cri, nearest_neighbors = costs_function_single_edge_static(storage = storage, edge = (u, v), time = route.timestamp_history[sindex], speed = route.speeds_history[sindex], visualize = True)
        color = "black"
        if "cri_threshold" in args:
          if cri >= args["cri_threshold"]:
            color = "red"
            alternatives = find_alternatives(alternatives = storage.results[storage.dot_config["algorithm_name"]][0][1], position = sindex, time = route.timestamp_history[sindex], cri = cri)
            for _u, _v in alternatives:
              map.add_child(folium.PolyLine([_u.coordinates, _v.coordinates], color = "green"))
        else:
          raise ValueError("@visualize: key \"cri_threshold\" not defined!")
        map.add_child(folium.PolyLine([u.coordinates, v.coordinates], color = color))
        for nearest_neighbor in nearest_neighbors:
          map.add_child(folium.CircleMarker([nearest_neighbor.lat, nearest_neighbor.lon], radius = 2, color = color))
    else:
      raise ValueError("@visualize: coloring invalid value!")
  else:
    raise ValueError("@visualize: mode invalid value!")
  map.save(f"{storage.path_root_code}/data/.result/.image/{file_name}.html")

# hidden short-hand function to parse a .csv file.
def build_skyline_routes(storage, dataframe, ball_tree, file_path, start_date):
  skyline_routes = []
  with open(file_path, 'r') as file:
    file_lines = file.readlines()[1:]
    for file_line in file_lines:
      tokens = file_line.replace(" ", "").split(",")[1:]
      source_node = algorithms.ARSC_FC.utils.data_structures.node.NODE(coordinates = (float(tokens[2]), float(tokens[3])))
      inputs_function(storage = storage, data = dataframe, ball_tree = ball_tree, node = source_node)
      path = algorithms.ARSC_FC.utils.data_structures.path.PATH(source_node = source_node, destination_node = source_node, costs_vector = [tokens[0], float(tokens[1])])
      path.speeds_history = []
      index = 5
      while index < len(tokens):
        node = algorithms.ARSC_FC.utils.data_structures.node.NODE(coordinates = (float(tokens[index]), float(tokens[index + 1])))
        inputs_function(storage = storage, data = dataframe, ball_tree = ball_tree, node = node)
        path.intermediate_nodes.append(node)
        path.speeds_history.append(float(tokens[index + 2]))
        index += 3
      path.update_timestamp_history(timestamp_history = [pd.Timestamp(start_date)])
      path.costs_vector_history = []
      index = 0
      while index < len(path.intermediate_nodes) - 1:
        time_delta, cri = costs_function_single_edge_static(storage = storage, edge = (path.intermediate_nodes[index], path.intermediate_nodes[index + 1]), time = path.timestamp_history[-1], speed = path.speeds_history[index])
        index += 1
        path.update_timestamp_history(timestamp_history = path.timestamp_history + [path.timestamp_history[-1] + pd.Timedelta(hours = time_delta)])
        path.costs_vector_history.append((time_delta, cri))
      path.destination_node = algorithms.ARSC_FC.utils.data_structures.node.NODE(coordinates = (float(tokens[-3]), float(tokens[-2])))
      skyline_routes.append(path)
  return None, skyline_routes

# main function.
if __name__ == "__main__":
  storage = state_storage.STATE_STORAGE()
  storage.path_root_code = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
  storage.raw_file_path = f"{storage.path_root_code}/.config/ARSC/ARSC.config"
  storage = IO.file_manager.FILE_MANAGER().read_dot_config(storage = storage)[1]
  storage.file_name = "ARSC"
  storage.results = {storage.dot_config["algorithm_name"]: []}

  path_ML_data = storage.dot_config["data"]["ML_data"]
  dataframe = pd.read_pickle(f"{storage.path_root_code}{path_ML_data}")
  ball_tree = BallTree(data = np.deg2rad(dataframe.geometry.get_coordinates())[["y", "x"]], leaf_size = 40, metric = "haversine")

  if MACRO_MULTIPLE_RUNS:
    file_CRI = open(f"{storage.path_root_code}/data/.result/.statistics/meta_data_CRI.evaluation", 'w', 1)
    file_CRI.write("|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
    file_CRI.write("| H3-resolution                          | timestamp                          | # of iteration                          | radius                          | # of edges (k)                          | cut-off                          |  source (latitude, longitude); destination (latitude, longitude)                          | # of paths                          | # of pruned paths                          | # of results                          | runtime (in seconds)(CRI)                          | runtime (in seconds) (Dijkstra)                          |\n")
    file_CRI.write("|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
    # file_Dijkstra = open(f"{storage.path_root_code}/data/.result/.statistics/meta_data_Dijkstra.evaluation", 'w', 1)
    # file_Dijkstra.write("|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
    # file_Dijkstra.write("| H3-resolution                          | timestamp                          | # of iteration                          | # of edges (k)                          | cut-off                          | result                          | runtime (in seconds)                          |\n")
    # file_Dijkstra.write("|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
    extension = "\n"
    for radius in MACRO_RADIUS:
      storage.dot_config["algorithm_parameter(s)"]["radius"] = radius
      for index, H3_resolution in enumerate(MACRO_H3_RESOLUTION):
        storage.dot_config["algorithm_parameter(s)"]["RNS_dimension"] = int((H3_resolution ** 2) / 4)
        if MACRO_FORCE_CREATE_GRAPH or not os.path.exists(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle"):
          storage.dot_config["algorithm_parameter(s)"]["H3_resolution"] = H3_resolution
          graph, _, _ = IO.file_manager.FILE_MANAGER().create_graph(create_function = algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().create_H3_saronic_golf_graph, storage = storage, dataframe = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/geoDataframe.pickle"))[1]
        else:
          graph = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle")
        for sindex, time in enumerate(MACRO_TIMESTAMPS):
          time = pd.to_datetime(time).asm8
          for iteration in range(MACRO_ITERATIONS):
            source_node, destination_node = sample(list(graph.nodes), 2)
            for k in MACRO_K:
              for cut_off in MACRO_CUT_OFF:
                storage.dot_config["algorithm_parameter(s)"]["cut_off"] = cut_off
                storage.file_name = f"H3.{H3_resolution:02}.index.{(iteration + 1):04}.radius.{radius:07.02f}.k.{k:02}.cut-off.{cut_off:05.02f} - from ({source_node.coordinates[0]:07.04f}, {source_node.coordinates[1]:07.04f}) to ({destination_node.coordinates[0]:07.04f}, {destination_node.coordinates[1]:07.04f})"
                # profiler = cProfile.Profile()
                # profiler.enable()
                embedding, skyline_routes, (overall_paths, pruned_paths, runtime_CRI) = algorithms.ARSC_FC.ARSC.ALGORITHM_ARSC().execute_algorithm(argument_vector = [storage, costs_function_single_edge_static, is_dominated_function, None, (graph, source_node, destination_node), time, generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), dataframe, ball_tree])[1]
                # profiler.disable()
                storage.results[storage.dot_config["algorithm_name"]].append((embedding, skyline_routes))
                IO.visualization_manager.VISUALIZATION_MANAGER().write_to_(write_function = algorithms.ARSC_FC.utils.IO.visualization_manager.VISUALIZATION_MANAGER().write_to_csv, storage = storage)
                visualize(storage = storage, file_name = storage.file_name, source_node = source_node, destination_node = destination_node)
                # pstats.Stats(profiler).dump_stats(f"{storage.path_root_code}/data/.result/.statistics/{storage.file_name}_CRI.dmp")
                # profiler = cProfile.Profile()
                # profiler.enable()
                shortest_path, runtime_Dijkstra = Dijkstra(graph = graph, source_node = source_node, destination_node = destination_node, start_date = time, speeds = generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), cut_off = cut_off) 
                # runtime = 0
                # for cut_off_Dijkstra in [value / 100.0 for value in range(0, 101, 1)]:
                #  shortest_path, runtime = Dijkstra(graph = graph, source_node = source_node, destination_node = destination_node, start_date = time, speeds = generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), cut_off = cut_off_Dijkstra)
                #  file_Dijkstra.write(f"| {H3_resolution:02}                                     | {MACRO_TIMESTAMPS[sindex]}                | {(iteration + 1):04}                                    | {k:02}                                      | {cut_off_Dijkstra:05.02f}                            | {shortest_path:011.02f}                     | {runtime:011.02f}                                   |\n")
                #  runtime_Dijkstra += runtime
                # file_Dijkstra.write("|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
                # file_Dijkstra.write("|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n")
                # profiler.disable()
                # pstats.Stats(profiler).dump_stats(f"{storage.path_root_code}/data/.result/.statistics/{storage.file_name}_Dijkstra.dmp")
                file_CRI.write(f"| {H3_resolution:02}                                     | {MACRO_TIMESTAMPS[sindex]}                | {(iteration + 1):04}                                    | {radius:07.02f}                         | {k:02}                                      | {cut_off:05.02f}                            | ({source_node.coordinates[0]:07.04f}, {source_node.coordinates[1]:07.04f}) ({destination_node.coordinates[0]:07.04f}, {destination_node.coordinates[1]:07.04f})                                                     | {overall_paths:08}                            | {pruned_paths:08}                                   | {len(skyline_routes):08}                              | {runtime_CRI:011.02f}                                        | {runtime_Dijkstra:011.02f}                                              |\n")
                if iteration + 1 == MACRO_ITERATIONS and index + 1 == len(MACRO_H3_RESOLUTION):
                  extension = ""
                file_CRI.write(f"|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|{extension}")
                # file_Dijkstra.write(f"|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|{extension}")
                storage.results[storage.dot_config["algorithm_name"]] = []
                for node in list(graph.nodes()):
                  node.sub_route_skyline = []
                  node.network_distance_estimations = []
      if MACRO_SAVE_GRAPH:
        pd.to_pickle(graph, f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle")
    file_CRI.close()
    # file_Dijkstra.close()
  else:
    H3_resolution = storage.dot_config["algorithm_parameter(s)"]["H3_resolution"]
    radius = storage.dot_config["algorithm_parameter(s)"]["radius"]
    if MACRO_FORCE_CREATE_GRAPH or not os.path.exists(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle"):
      graph, _, _ = IO.file_manager.FILE_MANAGER().create_graph(create_function = algorithms.ARSC_FC.utils.IO.file_manager.FILE_MANAGER().create_H3_saronic_golf_graph, storage = storage, dataframe = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/geoDataframe.pickle"))[1]
    else:
      # graph, _, _ = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle")
      graph = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle")
    source_node, destination_node = create_nodes(storage = storage, dataframe = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/geoDataframe.pickle"), ball_tree = ball_tree, graph = graph)
    if MACRO_SAVE_GRAPH:
      pd.to_pickle(graph, f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_graph.pickle")
    k = storage.dot_config["algorithm_parameter(s)"]["k"]
    cut_off = storage.dot_config["algorithm_parameter(s)"]["cut_off"]
    storage.file_name = f"H3.{H3_resolution:02}.radius.{radius:07.02f}.k.{k:02}.cut-off.{cut_off:05.02f} - from ({source_node.coordinates[0]:07.04f}, {source_node.coordinates[1]:07.04f}) to ({destination_node.coordinates[0]:07.04f}, {destination_node.coordinates[1]:07.04f})"
    # profiler = cProfile.Profile()
    # profiler.enable()
    if MACRO_CREATE_SKYLINE_ROUTES:
      embedding, skyline_routes, (overall_paths, pruned_paths, runtime_CRI) = algorithms.ARSC_FC.ARSC.ALGORITHM_ARSC().execute_algorithm(argument_vector = [storage, costs_function_single_edge_static, is_dominated_function, None, (graph, source_node, destination_node), pd.to_datetime(storage.dot_config["algorithm_parameter(s)"]["start_date"]).asm8, generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), dataframe, ball_tree])[1]
      if MACRO_SAVE_SKYLINE_ROUTES:
        pd.to_pickle((embedding, skyline_routes), f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_skyline_routes.pickle")
    if MACRO_LOAD_SKYLINE_ROUTES:
      storage.dot_config["data"]["ML_model"] = algorithms.ARSC_FC.utils.data_structures.ML_model.ML_MODEL().create_ML_model(storage = storage, ML_data = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/ARSC_results [0001].pickle"))
      embedding, skyline_routes = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_skyline_routes.pickle")
    if MACRO_PARSE_SKYLINE_ROUTES:
      storage.dot_config["data"]["ML_model"] = algorithms.ARSC_FC.utils.data_structures.ML_model.ML_MODEL().create_ML_model(storage = storage, ML_data = pd.read_pickle(f"{storage.path_root_code}/data/.ML_model/ARSC_results [0001].pickle"))
      embedding, skyline_routes = build_skyline_routes(storage = storage, dataframe = dataframe, ball_tree = ball_tree, file_path = f"{storage.path_root_code}/data/.result/.csv/{storage.file_name}_RF [0001].csv", start_date = pd.to_datetime(storage.dot_config["algorithm_parameter(s)"]["start_date"]).asm8)
      if MACRO_SAVE_SKYLINE_ROUTES:
        pd.to_pickle((embedding, skyline_routes), f"{storage.path_root_code}/data/.ML_model/H3.{H3_resolution:02}.radius.{radius:07.02f}_skyline_routes.pickle")
    # profiler.disable()
    storage.results[storage.dot_config["algorithm_name"]].append((embedding, skyline_routes))
    # IO.visualization_manager.VISUALIZATION_MANAGER().write_to_(write_function = algorithms.ARSC_FC.utils.IO.visualization_manager.VISUALIZATION_MANAGER().write_to_csv, storage = storage)
    visualize(storage = storage, file_name = storage.file_name + " - no_obstacles_and_no_RCI_grading", source_node = source_node, destination_node = destination_node, mode = "no_obstacles", coloring = "no_RCI_grading")
    visualize(storage = storage, file_name = storage.file_name + " - no_obstacles_and_RCI_grading", source_node = source_node, destination_node = destination_node, mode = "no_obstacles", coloring = "RCI_grading")
    visualize(storage = storage, file_name = storage.file_name + " - obstacles_and_no_RCI_grading", source_node = source_node, destination_node = destination_node, mode = "obstacles", coloring = "no_RCI_grading")
    visualize(storage = storage, file_name = storage.file_name + " - obstacles_and_RCI_grading", source_node = source_node, destination_node = destination_node, mode = "obstacles", coloring = "RCI_grading")
    visualize(storage = storage, file_name = storage.file_name + " - obstacles_and_partial_RCI_grading", source_node = source_node, destination_node = destination_node, mode = "obstacles", coloring = "partial_RCI_grading")
    # pstats.Stats(profiler).dump_stats(f"{storage.path_root_code}/data/.result/.statistics/{storage.file_name}_CRI.dmp")
    # profiler = cProfile.Profile()
    # profiler.enable()
    # shortest_path, runtime_Dijkstra = Dijkstra(graph = graph, source_node = source_node, destination_node = destination_node, start_date = pd.to_datetime(storage.dot_config["algorithm_parameter(s)"]["start_date"]).asm8, speeds = generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), cut_off = cut_off)
    runtime_Dijkstra = 0
    # for cut_off in [value / 100.0 for value in range(0, 101, 1)]:
    #  runtime_Dijkstra += Dijkstra(graph = graph, source_node = source_node, destination_node = destination_node, start_date = pd.to_datetime(storage.dot_config["algorithm_parameter(s)"]["start_date"]).asm8, speeds = generate_speeds_function(min = MACRO_SPEEDS[0], max = MACRO_SPEEDS[1], k = k), cut_off = cut_off)[1]
    # profiler.disable()
    # pstats.Stats(profiler).dump_stats(f"{storage.path_root_code}/data/.result/.statistics/{storage.file_name}_Dijkstra.dmp")
    if not MACRO_CREATE_SKYLINE_ROUTES:
      exit()
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    print("| H3-resolution                          | radius                          | # of edges (k)                          | cut-off                          |  source (latitude, longitude); destination (latitude, longitude)                          | # of paths                          | # of pruned paths                          | # of results                          | runtime (in seconds)(CRI)                          | runtime (in seconds) (Dijkstra)                          |\n")
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    print(f"| {H3_resolution:02}                                     | {radius:07.02f}                         | {k:02}                                      | {cut_off:05.02f}                            | ({source_node.coordinates[0]:07.04f}, {source_node.coordinates[1]:07.04f}) ({destination_node.coordinates[0]:07.04f}, {destination_node.coordinates[1]:07.04f})                                                     | {overall_paths:08}                            | {pruned_paths:08}                                   | {len(skyline_routes):08}                              | {runtime_CRI:011.02f}                                        | {runtime_Dijkstra:011.02f}                                              |\n")
    print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    exit()