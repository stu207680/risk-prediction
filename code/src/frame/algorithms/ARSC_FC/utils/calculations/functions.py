from algorithms.ARSC_FC.utils.calculations.CRI_C import calculate_cpa
from algorithms.ARSC_FC.utils.calculations.STT import initial_compass_bearing

from haversine import haversine
from shapely import Point

import numpy as np
import pandas as pd

MACRO_PRECISION_TIME = 3
MACRO_PRECISION_CRI = 2

MACRO_VISUALIZE_NN = 1000

def inputs_function(storage, data, ball_tree, node):
  node.data = data.iloc[ball_tree.query_radius(np.deg2rad([*node.coordinates]).reshape(1, -1), return_distance = False, sort_results = False, r = storage.dot_config["algorithm_parameter(s)"]["radius"] / (6371.0 * 1000.0))[0]]

def costs_function_single_edge_static(storage, edge, time, speed, dataframe = None, ball_tree = None, visualize = False):
  # calculates the time delta in hours:
  time_delta = round(haversine(edge[0].coordinates, edge[1].coordinates) / (1.852 * speed), MACRO_PRECISION_TIME)
  # determines the collision risk index:
  course = np.deg2rad(initial_compass_bearing(Point(edge[0].coordinates[1], edge[0].coordinates[0]), Point(edge[1].coordinates[1], edge[1].coordinates[0])))
  if ball_tree and not hasattr(edge[1], "data"):
    inputs_function(storage = storage, data = dataframe, ball_tree = ball_tree, node = edge[1])
  data = edge[1].data.loc[(edge[1].data["datetime"] >= time + pd.Timedelta(hours = time_delta) - pd.Timedelta(minutes = storage.dot_config["algorithm_parameter(s)"]["time_delta"])) & (edge[1].data["datetime"] < time + pd.Timedelta(hours = time_delta) + pd.Timedelta(minutes = storage.dot_config["algorithm_parameter(s)"]["time_delta"]))]
  cri_values = []
  for value in data.itertuples(index = False):
    dist, _, movement, azimuth_angle, _, _, _, _, _ = calculate_cpa(own = {"lat": edge[0].coordinates[0], "lon": edge[0].coordinates[1], "geometry": Point(edge[0].coordinates[1], edge[0].coordinates[0]), "speed": speed, "course_rad": course},
                                                                    target = {"lat": value.lat, "lon": value.lon, "geometry": value.geometry, "speed": value.speed, "course_rad": value.course_rad})
    cri_values.append((value, [speed, course, value.speed, value.course_rad, dist, movement, azimuth_angle]))
  cri = 0.0
  if not len(cri_values) == 0 and visualize:
    return time_delta, round(np.max(np.clip(storage.dot_config["data"]["ML_model"].predict(list(map(lambda x: x[1], cri_values))), 0, 1)), MACRO_PRECISION_CRI), list(map(lambda x: x[0], cri_values))[:MACRO_VISUALIZE_NN]
  elif not len(cri_values) == 0 and not visualize:
    return time_delta, round(np.max(np.clip(storage.dot_config["data"]["ML_model"].predict(list(map(lambda x: x[1], cri_values))), 0, 1)), MACRO_PRECISION_CRI)
  elif len(cri_values) == 0 and visualize:
    return time_delta, cri, []
  elif len(cri_values) == 0 and not visualize:
    return time_delta, cri

"""
purpose: Pareto-optimal function for the Advanced Route Skyline Computation (ARSC) algorithm.\n
I/O:
  - input: @sub_route should be checked if it is pareto-optimal.
           @routes contains all (currently) pareto-optimal route(s).
  - output: Either true if the (sub-)route is a pareto-optimal (sub-)route otherwise false.
"""
def is_dominated_function(sub_route, routes):
  for route in routes:
    dominated = True
    # checks if the given @sub_route is dominated by any other route from @routes:
    for attribute_dimension in range(len(route.costs_vector)):
      if sub_route.costs_vector[attribute_dimension] < route.costs_vector[attribute_dimension]:
        dominated = False
    if dominated:
      return False
  return True

# hidden short-hand function to remove dominated routes.
def clean_function(sub_route, routes, MACRO_PRUNED_PATHS):
  to_delete = []
  for route in routes:
    if not is_dominated_function(sub_route = route, routes = [sub_route]):
      to_delete.append(route)
      MACRO_PRUNED_PATHS += 1
  for delete in to_delete:
    routes.remove(delete)
  return MACRO_PRUNED_PATHS