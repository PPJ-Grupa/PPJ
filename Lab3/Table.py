from helpers import *

class Table:
  def __init__(self):
    self._contents = {}
  def contains(self, variable_name):
    return variable_name in self._contents
  def get_value(self,variable_name):
    return self._contents[variable_name]