"""
purpose: Global storage containing all necessary information.\n
"""
class STATE_STORAGE:
  """
  purpose: Creates a new state storage object.\n
  """
  def __init__(self):
    self.current_user = "unknown user"

    self.raw_file_path = None
    self.adjusted_file_path = None
    self.file_name = None

    self.file_loaded = False

    self.dot_config = None

    self.results = None

  """
  purpose: Resets all or specific values of this state storage object.\n
  I/O:
    - input: @current_user represents the current active user.
             @raw_file_path represents the original full file path.
             @adjusted_file_path represents file path that is displayed.
             @file_name represents the file name.
             @file_loaded represents the current state of the .config-file.
             @dot_config represents the .config-file.
             @results represents the previously stored result(s).
    - output: -/-
  """
  def clean(self, current_user = False, raw_file_path = False, adjusted_file_path = False, file_name = False, file_loaded = False, dot_config = False, results = False):
    if current_user:
      self.current_user = "unknown user"
    if raw_file_path:
      self.raw_file_path = None
    if adjusted_file_path:
      self.adjusted_file_path = None
    if file_name:
      self.file_name = None
    if file_loaded:
      self.file_loaded = False
    if dot_config:
      self.dot_config = None
    if results:
      self.results = None