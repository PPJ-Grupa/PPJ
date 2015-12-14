from helpers import *

class Expr:
  def __init__(self, etype, lexpr = False, 
      is_const = False, is_function = False,
      fun_from = [], fun_to = []):
   self._type = etype
   self._lexpr = lexpr
   self._const = is_const
   self._is_function = is_function
   self._function_from_types = fun_from
   self._function_to_types = fun_to
  def is_lexpr(self):
    return self._lexpr
  def is_type(self, etype):
    return self._type == etype
  def is_const(self):
    return self._const
  def is_int(self):
    return self._type == "INT"
  def is_function(self):
    return self._is_function
  def is_function_from(self, etype):
    return list(sorted(etype)) == \
      list(sorted(self._function_from_types))
  def is_function_to(self, etpye):
    return list(sorted(etype)) == \
      list(sorted(self._function_to_types))
  def get_type(self):
    return self._type
  def get_return_type(self):
    return self._function_to_types