from helpers import is_same_type
from Expr import Expr

class Table:
  def __init__(self):
    self._contents = {}
    self._declared_functions = {}
    self._defined_functions = {}
  def contains(self, variable_name):
    return variable_name in self._contents
  def get_var(self,variable_name):
    return self._contents[variable_name]
  def get_lexpr(self, variable_name):
    return self._contents[variable_name].get_lexpr()
  def get_type(self, variable_name):
    return self._contents[variable_name].get_type()

  #def add(self, entry):
  #  self._contents.append(entry)
  def declare_var(self, variable_name, var_type):
    self._contents[variable_name] = var_type
  def declare_fun(self, function_name, _fun_from, _fun_to):
    self._declared_functions[function_name] = \
      Expr("FUNCTION", is_function = True, fun_from = _fun_from, fun_to = _fun_to)
  def define(self, function_name, _fun_from, _fun_to):
    self._defined_functions[function_name] = \
      Expr("FUNCTION", is_function = True, fun_from = _fun_from, fun_to = _fun_to)

  def is_declared(self, variable_name, fun_from, fun_to):
    if not variable_name in self._declared_functions:
      return False
    else:
      expr = self._declared_functions[variable_name]
      return is_same_type(expr._function_from_types, fun_from) \
          and is_same_type(expr._function_to_types, fun_to)
  def is_defined(self, variable_name, fun_from, fun_to):
    if not variable_name in self._defined_functions:
      return False
    else:
      expr = self._defined_functions[variable_name]
      return is_same_type(expr._function_from_types, fun_from) \
          and is_same_type(expr._function_to_types, fun_to)
  def is_JUST_declared(self, variable_name):
    return variable_name in self._declared_functions

  def get_function(self, variable_name):
    if self.is_JUST_declared(variable_name):
      return self._declared_functions[variable_name]
    else:
      raise Exception("Function is not declared")

  def is_function_from(self, variable_name, etype):
    return self.get_function(variable_name).is_function_from(etype)
  def is_function_to(self, variable_name, etype):
    return self.get_function(variable_name).is_function_to(etype)