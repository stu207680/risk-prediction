from algorithms.ARSC_FC.utils.calculations.functions import inputs_function

import algorithms.ARSC_FC.utils.data_structures.node

import h3
import math
import networkx as nx
import numpy as np
import os
import pandas as pd
import pickle

"""
purpose: Common interface to save and load (a) savestate(s) for the Advanced Route Skyline Computation algorithm family.\n
"""
class FILE_MANAGER:
  """
  purpose: Creates a H3 Saronic Golf map and stores it into a NetworkX graph.\n
  I/O:
    - input: @storage stores the @H3_k_ring, @H3_resolution, @AC_value and @AS_dimension.
             @dataframe represents a pandas dataframe containing the data (optional).
    - output: Returns a NetworkX graph (containing the data).
  """
  def create_H3_saronic_golf_graph(self, storage, dataframe = None):
    # hidden short-hand function to map a node to the nearest data entry.
    def find_nearest_node(graph, coordinates):
      minimum = math.inf, None
      for node in list(graph.nodes()):
        distance = abs(node.coordinates[0] - coordinates[0]) + abs(node.coordinates[1] - coordinates[1])
        if minimum[0] > distance:
          minimum = distance, node
      return minimum[1]

    saronic_golf_map = dict()
    saronic_golf_map["type"] = "Polygon"
    saronic_golf_map["coordinates"] = [[[37.9359, 23.5847],
                                        [37.9253, 23.5469],
                                        [37.9122, 23.5346],
                                        [37.8960, 23.5156],
                                        [37.8810, 23.4678],
                                        [37.8181, 23.4653],
                                        [37.8215, 23.7454],
                                        [37.9321, 23.6748],
                                        [37.9252, 23.6321],
                                        [37.9336, 23.6218],
                                        [37.9410, 23.6179]]]
    saronic_golf_map = list(h3.polyfill(saronic_golf_map, storage.dot_config["algorithm_parameter(s)"]["H3_resolution"]))
    node_ID = 0
    graph = nx.DiGraph()
    buffer = dict()
    for node in saronic_golf_map:
      graph_node = algorithms.ARSC_FC.utils.data_structures.node.NODE(coordinates = h3.h3_to_geo(node))
      graph_node.ID = node_ID
      node_ID += 1
      buffer[node] = graph_node
      graph.add_node(graph_node)
    for node in saronic_golf_map:
      source_node = buffer[node]
      for neighbor in h3.k_ring_distances(node, storage.dot_config["algorithm_parameter(s)"]["H3_k_ring"])[storage.dot_config["algorithm_parameter(s)"]["H3_k_ring"]]:
        if neighbor in buffer and not node == neighbor:
          destination_node = buffer[neighbor]
          graph.add_edge(source_node, destination_node)
    return "@error: no error!", (graph, find_nearest_node(graph = graph, coordinates = storage.dot_config["algorithm_parameter(s)"]["source_node"]), find_nearest_node(graph = graph, coordinates = storage.dot_config["algorithm_parameter(s)"]["destination_node"]))

  """
  purpose: Saves the Lipschitz embedding.\n
  I/O:
    - input: @storage stores the @embedding and @preserve_data.
             @embedding represents the Lipschitz embedding which should be stored.
             @graph represents the NetworkX graph within the nodes are stored.
    - output: -/-
  """
  def save_embedding(self, storage, embedding, graph):
    embedding_ID = len(storage.results[storage.dot_config["algorithm_name"]])
    if storage.dot_config["algorithm_parameter(s)"]["preserve_data"]:
      for node in list(graph.nodes()):
        node.sub_route_skyline = []
    pickle.dump((embedding, graph), open(f"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))}/data/.embedding/{storage.file_name}_embedding [{embedding_ID + 1:04d}].embedding", "wb"))

  """
  purpose: Loads a Lipschitz embedding.\n
  I/O:
    - input: @storage stores the file path to the Lipschitz embedding.
    - output: Returns a Lipschitz embedding and the corresponding graph.
  """
  def load_embedding(self, storage):
    return "@error: no error!", pd.read_pickle(storage.dot_config["data"]["embedding"])

  """
  purpose: Saves the machine learning model.\n
  I/O:
    - input: @storage stores the @ML_model.
             @ML_model represents the machine learning model which should be stored.
    - output: -/-
  """
  def save_ML_model(self, storage, ML_model):
    ML_model_ID = len(storage.results[storage.dot_config["algorithm_name"]])
    pickle.dump(ML_model, open(f"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))))}/data/.ML_model/{storage.file_name}_ML_model [{ML_model_ID + 1:04d}].ML_model", "wb"))

  """
  purpose: Loads a machine learning model.\n
  I/O:
    - input: @storage stores the file path to the machine learning model.
    - output: Returns a machine learning model.
  """
  def load_ML_model(self, storage):
    return "@error: no error!", pd.read_pickle(storage.dot_config["data"]["ML_model"])