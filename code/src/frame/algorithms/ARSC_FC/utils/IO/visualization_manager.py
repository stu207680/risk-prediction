"""
purpose: Common interface for working with I/O for the Advanced Route Skyline Computation algorithm family.\n
"""
class VISUALIZATION_MANAGER:
  """
  purpose: Write the data into a .csv file.\n
  I/O:
    - input: @storage stores the @results.
    - output: -/-
  """
  def write_to_csv(self, storage):
    file_id = len(storage.results[storage.dot_config["algorithm_name"]]) - 1
    path_write_to = storage.dot_config["data"]["path_write_to"]
    with open(f"{storage.path_root_code}{path_write_to}{storage.file_name}_RF [{file_id + 1:04d}].csv", 'w') as file:
      for index, (_, routes) in enumerate(storage.results[storage.dot_config["algorithm_name"]]):
        padding = 0
        for route in routes:
          if padding < len(route.intermediate_nodes):
            padding = len(route.intermediate_nodes)
        for sindex, route in enumerate(routes):
          if sindex == 0:
            buffer = "id"
            for SI_measurement in storage.dot_config["algorithm_parameter(s)"]["SI_measurement(s)"]:
              buffer += f", {SI_measurement.name}"
            if padding > 0:
              file.write(buffer + (f", latitude, longitude, speed" * padding) + '\n')
            else:
              file.write(buffer + '\n')
          buffer = f"{index + 1:04d}.{sindex + 1:04d}, "
          for tindex, costs_vector in enumerate(route.costs_vector):
            if tindex == 0:
              buffer += f"{abs(route.timestamp_history[0].day - route.timestamp_history[-1].day):02d}:{abs(route.timestamp_history[0].hour - route.timestamp_history[-1].hour):02d}:{abs(route.timestamp_history[0].minute - route.timestamp_history[-1].minute):02d}:{abs(route.timestamp_history[0].second - route.timestamp_history[-1].second):02d}, "
            else:
              buffer += f"{costs_vector:06.02f}, "
          buffer += f"{route.source_node.coordinates[0]:06.4f}, {route.source_node.coordinates[1]:07.4f}, -/-, "
          for tindex, intermediate_node in enumerate(route.intermediate_nodes):
            if tindex == 0 or tindex == len(route.intermediate_nodes) - 1:
              continue
            buffer += f"{intermediate_node.coordinates[0]:06.4f}, {intermediate_node.coordinates[1]:07.4f}, {route.speeds_history[tindex]:07.4f}, "
          buffer += f"{route.destination_node.coordinates[0]:06.4f}, {route.destination_node.coordinates[1]:07.4f}, {route.speeds_history[-1]:07.4f}"
          if sindex + 1 < len(routes):
            buffer += '\n'
          file.write(buffer)
        if index + 1 < len(storage.results[storage.dot_config["algorithm_name"]]):
          file.write("\n\n")