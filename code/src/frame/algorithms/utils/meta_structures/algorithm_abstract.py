import abc

"""
purpose: Common abstraction for all members of the class @ALGORITHM_*.\n
"""
class ALGORITHM_ABSTRACT(abc.ABC):
  """
  purpose: Executes the <ALGORITHM_NAME> algorithm.\n
  I/O:
    - input: @argument_vector represents the argument vector containing all necessary information to execute the algorithm.
    - output: Returns either the result of the algorithm or an error message.
  """
  @abc.abstractmethod
  def execute_algorithm(self, **argument_vector):
    pass