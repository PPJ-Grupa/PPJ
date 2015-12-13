from helpers import *

class Expr:
  def __init__(self, etype, lexpr = False):
   self._type = etype
   self._lexpr = lexpr
  def is_lexpr(self):
    return self._lexpr
  def is_type(self, etype):
    return self._type == etype