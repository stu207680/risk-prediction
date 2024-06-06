import os

"""
purpose: Common interface for working with I/O.\n
"""
class VISUALIZATION_MANAGER:
  """
  purpose: Write the data into a given file format.\n
  I/O:
    - input: @write_function determines how the @results should be written into a file format.
             @storage stores the @results.
    - output: Returns either nothing or an error message.
  """
  def write_to_(self, write_function, storage):
    # if not (os.path.exists(storage.dot_config["data"]["path_write_to"]) and os.path.isdir(storage.dot_config["data"]["path_write_to"])):
    #   return "@error: no path found to store the result!", None
    return "@error: no error!", write_function(storage = storage)