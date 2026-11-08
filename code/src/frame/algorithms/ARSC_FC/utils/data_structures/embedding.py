from haversine import haversine

import math
import queue
import random

"""
purpose: Common interface for the Lipschitz embedding for the Advanced Route Skyline Computation algorithm family.\n
"""
class EMBEDDING:
  """
  purpose: Creates a Lipschitz embedding.\n
  I/O:
    - input: @storage stores the @RNS_dimension and @multiple_edge(s).
             @data contains the data.
             @graph represents the NetworkX graph within the nodes are stored.
    - output: Returns a Lipschitz embedding.
  """
  def create_embedding(self, storage, graph):
    # hidden short-hand function to calculate the shortest distance between two nodes using Dijkstra's algorithm.
    def Dijkstra(storage, graph, source_node):
      embedding = dict()
      priority_queue = queue.PriorityQueue()

      priority_queue.put((0.0, source_node))
      while not priority_queue.empty():
        embedding_cost, u_node = priority_queue.get()
        if not u_node.ID in embedding:
          embedding[u_node.ID] = math.inf
        elif not embedding[u_node.ID] == math.inf:
          continue
        embedding[u_node.ID] = embedding_cost
        for edge in graph.edges(u_node, data = True):
          v_node = edge[1]
          if v_node.ID in embedding and not embedding[v_node.ID] == math.inf:
            continue
          cost_delta = haversine(v_node.coordinates, u_node.coordinates) / (1.852 * storage.dot_config["algorithm_parameter(s)"]["speed"])
          if cost_delta != math.inf:
            priority_queue.put((embedding_cost + cost_delta, v_node))
      return embedding

    reference_nodes = list(graph.nodes())
    random.shuffle(reference_nodes)
    reference_nodes = reference_nodes[:storage.dot_config["algorithm_parameter(s)"]["RNS_dimension"]]
    embedding = dict()
    # initialization of a Lipschitz embedding:
    for reference_node in reference_nodes:
      if not reference_node.ID in embedding:
        embedding[reference_node.ID] = dict()
      embedding[reference_node.ID] = Dijkstra(storage = storage, graph = graph, source_node = reference_node)
    return embedding