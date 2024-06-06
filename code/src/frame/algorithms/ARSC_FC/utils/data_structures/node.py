import math

"""
purpose: Class for representing a graph node object for the Advanced Route Skyline Computation algorithm family.\n
"""
class NODE:
  """
  purpose: Instanced a new node object.\n
  I/O:
    - input: @coordinates represents the unique identifier for this node object.
             @data contains the data which should be stored onto this node object (optional).
    - output: -/-
  """
  def __init__(self, coordinates, ID = 0):
    self.coordinates = coordinates

    self.ID = ID

    self.sub_route_skyline = []

    self.network_distance_estimations = []

  """
  purpose: Updates the sub route skyline for this node object.\n
  I/O:
    - input: @sub_route represents a new sub route which belongs to this node object.
    - output: -/-
  """
  def update_sub_route_skyline(self, sub_route):
    self.sub_route_skyline.append(sub_route)

  """
  purpose: Ensure an unique hash value for each node object.\n
  I/O:
    - input: -/-
    - output: Returns a hash value for this node object.
  """
  def __hash__(self):
    return hash(repr(self))

  """
  purpose: Enables the less than relation between two node objects. Intended use only for tie breaking. Just compares node IDs!\n
  I/O:
    - input: @other_node represents a node object which should be set in relation to this node object.
    - output: Either true if the this node object is less than the other node object, otherwise false.
  """
  def __lt__(self, other_node):
    return self.ID < other_node.ID

  """
  purpose: Enables the equal relation between two node objects.\n
  I/O:
    - input: @other_node represents a node object which should be set in relation to this node object.
    - output: Either true if this node object is equal to the other node object, otherwise false.
  """
  def __eq__(self, other_node):
    return self.ID == other_node.ID

  """
  purpose: Enables the less than or equal relation between two node objects.\n
  I/O:
    - input: @other_node represents a node object which should be set in relation to this node object.
    - output: Either true if this node object is less than or equal to the other node object, otherwise false.
  """
  def __le__(self, other_node):
    return self == other_node or self < other_node
  
  """
  purpose: Computes a score for comparing nodes by calculation sums of the attribute vectors of this nodes sub skylines and yielding the minimum of these.\n
  I/O:
    - input: -/-
    - output: Returns the score for comparing nodes based on their sub_skylines.
  """
  def min_score(self):    
    if not self.sub_route_skyline:
      min_score  = math.inf
    else:
      min_score = min(list(map(lambda sub_route: sub_route.attributes_vector[0], self.sub_route_skyline)))
    return min_score