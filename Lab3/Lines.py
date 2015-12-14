from helpers import *

class Lines:
  def __init__(self, lines):
    self._lines = lines
    self._iter = 0
  """Check whether iter is out of bounds"""
  def iter_outside(self):
    return self._iter < 0 or self._iter >= len(self._lines)
  """Move iter to next line"""
  def next(self):
    self._iter += 1
    return
  """Get current line"""
  def get_line(self, iterr = -1):
    if iterr == -1:
      return self._lines[self._iter]
    else:
      return self._lines[iterr]
  """Get padding depth of current line"""
  def get_lvl(self, iterr = -1):
    ret, _ = chop(self.get_line(iterr))
    return int(ret)
  """Returns the next expression on the current depth lvl"""
  def next_in_lvl(self, original_lvl):
    self.next()
    #print("next_in_lvl getline: " + self.get_line())
    while not self.iter_outside() and self.get_lvl() != original_lvl:
      self.next()
    _, expr, _ = extract_3(self.get_line())
    #print("next: " + str(expr))
    return expr
  """Check whether provided expressions exist at the current level"""
  def check_expressions(self, expressions):
    original_iter = self._iter
    original_lvl = self.get_lvl()
    print("orig lvl: " + str(original_lvl))
    print("expressions: " + str(expressions))
    for expr in expressions:
      #print("expr: " + expr)
      next_in_lv = self.next_in_lvl(original_lvl + 1)
      if not next_in_lv == expr:
        self._iter = original_iter
        print("next in lvl (fls): " + next_in_lv)
        return False
    self._iter = original_iter
    self.next()
    return True