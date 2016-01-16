from helpers import *

class Expr:
  def __eq__(self, other):
    # and self.is_const == other.is_const \ can be implicitly converted
    # and self.is_lexpr == other.is_lexpr \    
    return isinstance(other, self.__class__) \
        and (self._type == other._type \
          or self._type == "INT" and other._type == "CHAR" \
          or self._type == "CHAR" and other._type == "INT") \
        and self.is_array == other.is_array and self.is_function == other.is_function \
        and self._function_from_types == other._function_from_types \
        and self._function_to_types == other._function_to_types
  def __gt__(self, other):
    return self._type > other._type or  self.is_lexpr  > other.is_lexpr \
        or self.is_array > other.is_array or self.is_function > other.is_function \
        or self._function_from_types > other._function_from_types \
        or self._function_to_types > other._function_to_types 
  def __str__(self):
    ret = "Expr: t: " + self._type + ", le: " + str(self.is_lexpr) + ", arr: " + \
        str(self.is_array) + ", con: " + str(self.is_const) + ", f: " + \
        str(self.is_function)
    ret = ret + "\nfrom: "
    for expr in self._function_from_types:
      ret = ret + "\n:: " + str(expr)
    ret = ret + "\nto: "
    for expr in self._function_to_types:
      ret = ret + "\n:: " + str(expr)
    return ret

  def __init__(self, etype, 
      is_lexpr = False, is_const = False, is_function = False, is_array = False,
      fun_from = [], fun_to = [],
      array_length = -1):
    if type(etype) is list:
      raise Exception("This should not be list!")
    if not type(fun_from) is list:
      raise Exception("fun_from not list")
    if not type(fun_to) is list:
      raise Exception("fun_to not list")
    if type(etype) is Expr:
      self._type = etype._type
      self.is_lexpr = etype.is_lexpr
      self.is_const = etype.is_const
      self.is_array = etype.is_array
      self.is_function = etype.is_function
      self._function_from_types = etype._function_from_types
      self._function_to_types = etype._function_to_types
      # A bit hackysh implementation for <inicijalizator>
      self.array_length = etype.array_length
    else:
      self._type = etype
      self.is_lexpr = is_lexpr
      self.is_const = is_const
      self.is_array = is_array
      self.is_function = is_function
      self._function_from_types = fun_from
      self._function_to_types = fun_to
      self.array_length = array_length
  """IS X"""
  def is_type(self, expr):
    raise Exception("Check is_type usages")
    if type(expr) is list:
      return False
    elif type(expr) is self.__class__:
      return self == expr
    else:
      raise Exception("Invalid comparison")

  def is_function_from(self, etypes):
    if not type(etypes) is list:
      raise Exception("Make listy")
    return list(sorted(etypes)) == \
      list(sorted(self._function_from_types))
  def is_function_to(self, etypes):
    if not type(etypes) is list:
      raise Exception("Make listy")
    return list(sorted(etypes)) == \
      list(sorted(self._function_to_types))
  """GET X"""
  def get_type(self):
    raise Exception("Check get_type usages")
    return self._type
  def get_return_type(self):
    return self._function_to_types
  """SET X"""
  def set_to_array(self):
    self.is_array = True
    return self
  def set_to_const(self):
    self.is_const = True
    return self
  def set_to_lexpr(self):
    self.is_lexpr = True
    return self