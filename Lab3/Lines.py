from helpers import *
from Expr import Expr

class Lines:
  def __init__(self, lines):
    self._lines = lines
    self._iter = 0
    self.terminate = False
  """Check whether iter is out of bounds"""
  def iter_outside(self):
    return self._iter < 0 or self._iter >= len(self._lines)
  """Move iter to next line"""
  def next(self):
    self._iter += 1
    return
  """Move iter to previouos line"""
  def prev(self):
    self._iter -= 1
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
  """Returns the next expression on the target depth lvl"""
  def next_in_lvl(self, target_lvl):
    self.next()
    ##print("next_in_lvl getline: " + self.get_line())
    while not self.iter_outside() and self.get_lvl() != target_lvl:
      self.next()
    _, expr, _ = extract_3(self.get_line())
    ##print("next: " + str(expr))
    return expr
  """Returns the previous expression on the target depth lvl"""
  def prev_in_lvl(self, target_lvl):
    self.prev()
    while not self.iter_outside() and self.get_lvl() != target_lvl:
      self.prev()
    _, expr, _ = extract_3(self.get_line())
    return expr
  """Check whether provided expressions exist at the current level"""
  def check_expressions(self, expressions):
    original_iter = self._iter
    original_lvl = self.get_lvl()
    ##print("orig lvl: " + str(original_lvl))
    ##print("expressions: " + str(expressions))
    for expr in expressions:
      #print("expr: " + expr)
      next_in_lv = self.next_in_lvl(original_lvl + 1)
      if not next_in_lv == expr:
        self._iter = original_iter
        #print("next in lvl (fls): " + next_in_lv)
        return False
    self._iter = original_iter
    self.next()
    return True

  """Assert leaf"""
  def assert_leaf(self, fst_exp, snd_exp = ""):
    print("# assert_leaf: " + fst_exp)
    print(self.get_line())
    _, _fst_exp, _, _snd_exp = extract_4(self.get_line())
    #if fst_exp == "D_VIT_ZAGRADA": raise Exception()
    if not _fst_exp == fst_exp:
      print("fs: " + fst_exp + " _: " + _fst_exp)
      return self.parse_error()
    if not _snd_exp == snd_exp and not snd_exp == "":
      return self.parse_error()
    else:
      self.next()
      return _snd_exp

  """Parse error"""
  def parse_error(self):
    #raise Exception() # <naredba_grananja> ::= KR_IF(4,if) L_ZAGRADA(4,() <izraz> D_ZAGRADA(4,)) <naredba>
    if self.terminate:
      return
    #print(self.get_line())
    #self.lines._iter -= 1
    #_, exp, line_num, name = extract_4(self.lines.get_line())
    current_lvl = self.get_lvl()
    prev_expr = self.prev_in_lvl(current_lvl - 1)
    #self.lines.next()
    final_output = prev_expr + " ::="
    self.next()
    while not self.iter_outside() and self.get_lvl() > current_lvl - 1:
      #print()
      if self.get_lvl() == current_lvl:
        _, exp, line_num, name = extract_4(self.get_line())
        if line_num == "" and name == "":
          final_output = final_output + " " + exp
        else:
          final_output = final_output + " " + exp + "(" + line_num + "," + name + ")"
      self.next()
    print(final_output)
    self.terminate = True
    #print(prev_expr + " ::= " + exp + "(" + line_num + "," + name + ")")
    #raise Exception()
    return Expr("TEMINATE")