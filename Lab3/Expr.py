from helpers import *

class Expr:
  def __init__(self, etype, lexpr = False, is_const = False):
   self._type = etype
   self._lexpr = lexpr
   self._const = is_const
  def is_lexpr(self):
    return self._lexpr
  def is_type(self, etype):
    return self._type == etype
  def is_const(self):
    return self._const
  def is_int(self):
    return self._type == "INT"

  def get_type(self):
    return self._type