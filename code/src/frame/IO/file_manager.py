from algorithms.utils.definitions.SI_measurement import SI_RISK_OF_COLLISION, SI_MASS, SI_TIME

import os

"""
purpose: Common interface for working with file(s).\n
"""
class FILE_MANAGER:
  """
  purpose: Parses the .config-file.\n
  I/O:
    - input: @storage stores all relevant information.
    - output: Returns either a storage containing the parsed .config data or an error message.
  """
  def read_dot_config(self, storage):
    # hidden short-hand function to parse constant symboles.
    def parse_constants(input):
      constants = [
          ("True", True), ("true", True), ("False", False), ("false", False),
          ("undefined", None),
          ("SI_RISK_OF_COLLISION.SI_RISK_OF_COLLISION", SI_RISK_OF_COLLISION.SI_RISK_OF_COLLISION),
          ("SI_MASS.SI_GRAM", SI_MASS.SI_GRAM), ("SI_MASS.SI_KILOGRAM", SI_MASS.SI_KILOGRAM), ("SI_MASS.SI_METRIC_TON", SI_MASS.SI_METRIC_TON),
          ("SI_TIME.SI_SECOND", SI_TIME.SI_SECOND), ("SI_TIME.SI_MINUTE", SI_TIME.SI_MINUTE), ("SI_TIME.SI_HOUR", SI_TIME.SI_HOUR), ("SI_TIME.SI_DAY", SI_TIME.SI_DAY), ("SI_TIME.SI_WEEK", SI_TIME.SI_WEEK), ("SI_TIME.SI_YEAR", SI_TIME.SI_YEAR)]
      for constant, value in constants:
        if input.lower() == constant.lower():
          return value
      return "no constant found!"

    if not (os.path.exists(storage.raw_file_path) and os.path.isfile(storage.raw_file_path)):
      return "@error: .config-file not found!", storage
    file = open(storage.raw_file_path, 'r')
    if not storage.dot_config:
      storage.dot_config = dict()
    is_nested = False
    nested_value = None
    for file_line in file:
      file_line = file_line.split(" # ")[0]
      if file_line.replace(' ', '').replace('\n', '') == "" or file_line.replace(' ', '')[0] == '#':
        continue
      # ignores newlines, tabs and parses the line
      file_line = file_line.replace("    ", '').replace('\n', '')
      if '{' in file_line:
        # parses the line
        inputs = file_line.split(" # ")
        inputs = inputs[0].split(':')
        # ignores unnecessary characters and parses the key of the key-value pair
        key = inputs[0].replace('.', '').replace(' ', '')
        storage.dot_config[key] = dict()
        is_nested = True
        nested_value = key
      elif '=' in file_line:
        inputs = file_line.split(" # ")
        inputs = inputs[0].split(" = ")
        key = inputs[0].replace('.', '').replace(' ', '')
        # checks if the lines is incomplete:
        if len(inputs) != 2:
          storage.clean(file_loaded = True, dot_config = True)
          return "@error: .config-file incomplete!", storage
        # checks if the current line is a constant:
        result = parse_constants(input = inputs[1].replace(' ', ''))
        if not result == "no constant found!":
          inputs[1] = result
        # checks if the current line is a string:
        elif inputs[1].replace(' ', '').isdecimal():
          inputs[1] = int(inputs[1])
        # checks if the current line is a list:
        elif '[' == inputs[1][0] and ']' == inputs[1][len(inputs[1]) - 1]:
          # checks if the current list is empty:
          if len(inputs[1].replace(' ', '')) == 2:
            inputs[1] = []
          else:
            parsed = True
            # ignores unnecessary characters and parses the value (list element(s)) of the key-value pair
            if not '\"' in inputs[1]:
              inputs[1] = inputs[1].replace(' ', '')
            inputs[1] = inputs[1].replace('[', '').replace(']', '').split(',')
            inputs[1] = list(inputs[1])
            parsed_values = []
            for input in inputs[1]:
              result = parse_constants(input = input)
              # checks if the current value is a constant:
              if not result == "no constant found!":
                parsed_values.append(("constant", result))
              # checks if the current value is a string:
              elif " \"" in input:
                parsed_values.append(("string", input.replace(" \"", '').replace('\"', '')))
              elif '\"' in input:
                parsed_values.append(("string", input.replace('\"', '')))
              # checks if the current value is an integer:
              elif input.isdecimal():
                parsed_values.append(("integer", int(input)))
              # checks if the current value is a float:
              else:
                try:
                  parsed_values.append(("float", float(input)))
                except ValueError:
                  parsed = False
                  break
            if parsed:
              # checks if all value are from the same type:
              if len(list(filter(lambda x: x[0] == "constant", parsed_values))) == len(inputs[1]):
                inputs[1] = list(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "string", parsed_values))) == len(inputs[1]):
                inputs[1] = list(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "integer", parsed_values))) == len(inputs[1]):
                inputs[1] = list(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "float", parsed_values))) == len(inputs[1]):
                inputs[1] = list(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "integer", parsed_values))) + len(list(filter(lambda x: x[0] == "float", parsed_values))) == len(inputs[1]):
                inputs[1] = list(map(lambda x: x[1], parsed_values))
              else:
                storage.clean(file_loaded = True, dot_config = True)
                return "@error: .config-file contains value mismatch!", storage
        elif '(' == inputs[1][0] and ')' == inputs[1][len(inputs[1]) - 1]:
          if len(inputs[1].replace(' ', '')) == 2:
            inputs[1] = tuple()
          else:
            parsed = True
            if not '\"' in inputs[1]:
              inputs[1] = inputs[1].replace(' ', '')
            inputs[1] = inputs[1].replace('(', '').replace(')', '').split(',')
            inputs[1] = tuple(inputs[1])
            parsed_values = []
            for input in inputs[1]:
              result = parse_constants(input = input)
              if not result == "no constant found!":
                parsed_values.append(("constant", result))
              elif " \"" in input:
                parsed_values.append(("string", input.replace(" \"", '').replace('\"', '')))
              elif '\"' in input:
                parsed_values.append(("string", input.replace('\"', '')))
              elif input.isdecimal():
                parsed_values.append(("integer", int(input)))
              else:
                try:
                  parsed_values.append(("float", float(input)))
                except ValueError:
                  parsed = False
                  break
            if parsed:
              if len(list(filter(lambda x: x[0] == "constant", parsed_values))) == len(inputs[1]):
                inputs[1] = tuple(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "string", parsed_values))) == len(inputs[1]):
                inputs[1] = tuple(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "integer", parsed_values))) == len(inputs[1]):
                inputs[1] = tuple(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "float", parsed_values))) == len(inputs[1]):
                inputs[1] = tuple(map(lambda x: x[1], parsed_values))
              elif len(list(filter(lambda x: x[0] == "integer", parsed_values))) + len(list(filter(lambda x: x[0] == "float", parsed_values))) == len(inputs[1]):
                inputs[1] = tuple(map(lambda x: x[1], parsed_values))
              else:
                storage.clean(file_loaded = True, dot_config = True)
                return "@error: .config-file contains value mismatch!", storage
        elif '\"' in inputs[1]:
          inputs[1] = inputs[1].replace('\"', '')
        else:
          try:
            inputs[1] = float(inputs[1].replace(' ', ''))
          except ValueError:
            storage.clean(file_loaded = True, dot_config = True)
            return "@error: .config-file could not be parsed!", storage
        if not is_nested:
          storage.dot_config[key] = inputs[1]
        else:
          storage.dot_config[nested_value][key] = inputs[1]
      elif '}' in file_line:
        is_nested = False
        nested_value = None
      else:
        storage.clean(file_loaded = True, dot_config = True)
        return "@error: .config-file could not be parsed!", storage
    return "@error: no error!", storage

  """
  purpose: Creates a NetworkX graph.\n
  I/O:
    - input: @create_function determines how the @dataframe is transformed into a NetworkX graph.
             @storage stores the @H3_k_ring, @H3_resolution, @AC_value and @AS_dimension.
             @dataframe represents a pandas dataframe containing the data.
    - output: Returns either a NetworkX graph containing the data or an error message.
  """
  def create_graph(self, create_function, storage, dataframe):
    return create_function(storage = storage, dataframe = dataframe)