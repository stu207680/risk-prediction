"""
purpose: Class for representing a path (of a graph) object for the Advanced Route Skyline Computation algorithm family.\n
"""
class PATH:
  """
  purpose: Instanced a new path object.\n
  I/O:
    - input: @source_node represents the source node of this path (begin of the path) object.
             @destination_node represents the destination node of this path (end of the path) object.
             @cost_vector represents the cost(s) of this path object.
    - output: -/-
  """
  def __init__(self, source_node, destination_node, costs_vector):
    self.source_node = source_node
    self.intermediate_nodes = [destination_node]
    self.destination_node = destination_node

    self.costs_vector = costs_vector

    self.processed = False

  """
  purpose: Updates the intermediate node(s) between the source and destination node of this path object.\n
  I/O:
    - input: @intermediate_nodes represents the sub path between the source and destination node.
    - output: -/-
  """
  def update_intermediate_nodes(self, intermediate_nodes):
    self.intermediate_nodes = intermediate_nodes + self.intermediate_nodes

  """
  purpose: Updates the timestamp history of this path object.\n
  I/O:
    - input: @timestamp_history represents the new timestamp history of this path object.
    - output: -/-
  """
  def update_timestamp_history(self, timestamp_history):
    self.timestamp_history = timestamp_history

  """
  purpose: Calculates the lower bound of this path object using Kriegel et al.'s estimation.\n
  I/O:
    - input: @embedding represents the Lipschitz embedding.
             @destination_node represents the overall destination (final destination of this path object).
    - output: -/-
  """
  def calculate_attributes_vector(self, embedding, destination_node):
    # short-hand function to calculate the network distance.
    def calculate_network_distance_estimations(embedding, source_node, destination_node):
      network_distance_estimations = []
      for reference_node_id in embedding:
        try:
          network_distance_estimations.append(abs(embedding[reference_node_id][source_node.ID] - embedding[reference_node_id][destination_node.ID]))
        except:
          pass        
      return max(network_distance_estimations)
  
    if not self.destination_node.network_distance_estimations:
      self.destination_node.network_distance_estimations = calculate_network_distance_estimations(embedding = embedding, source_node = self.destination_node, destination_node = destination_node)
    self.attributes_vector = [self.costs_vector[0] + self.destination_node.network_distance_estimations, self.costs_vector[1]]