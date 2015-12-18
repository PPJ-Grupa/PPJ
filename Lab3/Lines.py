from helpers import *
from Expr import Expr

def pprint(stri):
  return
  print(stri)

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
    ## Check for out of range
    if iterr >= len(self._lines) or \
        iterr == -1 and self._iter >= len(self._lines):
      return self.get_line(0)
    ## Whether you want specific line (iterr specified) or not
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
    while not self.iter_outside() and self.get_lvl() > target_lvl:
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
    #pprint("check: " + str(expressions))
    original_iter = self._iter
    original_lvl = self.get_lvl()
    #print(self.get_lvl())
    #print(self.get_line())
    ##print("orig lvl: " + str(original_lvl))
    ##print("expressions: " + str(expressions))
    for expr in expressions:
      #print("expr: " + expr)
      next_in_lv = self.next_in_lvl(original_lvl + 1)
      if not next_in_lv == expr:
        self._iter = original_iter
        #pprint("should: " + expr + " but next in lvl (fls): " + next_in_lv)
        return False
    ##check whether there should be a "bigger" production
    #print("debo")
    #print(original_lvl)
    #print(self.get_line())
    self.next_in_lvl(original_lvl + 1)
    if self.get_lvl() == original_lvl + 1:
      self._iter = original_iter
      return False
    #print(self.get_lvl())
    #print(self.get_line())
    ## Reset iterator to previous (starting position) (since check_expressions)
    self._iter = original_iter
    self.next()
    #pprint("accepted: " + str(expressions))
    return True

  """Assert leaf"""
  def assert_leaf(self, fst_exp, snd_exp = ""):
    curr_line = self._iter
    pprint("# assert_leaf: " + fst_exp)
    pprint(self.get_line())
    _, _fst_exp, _, _snd_exp = extract_4(self.get_line())
    #if fst_exp == "D_VIT_ZAGRADA": raise Exception()
    if not _fst_exp == fst_exp:
      #pprint("fs: " + fst_exp + " _: " + _fst_exp)
      return self.parse_error(curr_line)
    if not _snd_exp == snd_exp and not snd_exp == "":
      return self.parse_error(curr_line)
    else:
      self.next()
      return _snd_exp

  """Parse error"""
  def parse_error(self, curr_line):
    #raise Exception("Parse error")
    #print(str(self.terminate))
    if self.terminate:
      return
    self._iter = curr_line + 1
    #self.prev()
    pprint("line: " + self.get_line())
    pprint("lvl: " + str(self.get_lvl()))
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
    return Expr("TEMINATE") #, Expr("TEMINATE"), Expr("TEMINATE")