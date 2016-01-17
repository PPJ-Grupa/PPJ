from FinalCodeGenerator import *
from OutputCode import *
'''
ideja je da u ovom fajlu pisemo dijelove analogne onima iz FileCodeGeneratora
koji generiraju kod
Ono iz jave da postoji vise fajlova, paketa i klasa nije bas tako losa praksa.
'''
'''
outputCode = OutputCode()
currFunction = 'F_MAIN' #u koju funkciju trenutno zapisujemo naredbe

"""NAREDBA SKOKA"""
def naredba_skoka(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
    pprint("# naredba_skoka")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_CONTINUE", "TOCKAZAREZ"]):
      if not in_loop:
        return self.parse_error(curr_line)
      self.assert_leaf("KR_CONTINUE")
      self.assert_leaf("TOCKAZAREZ")
      return
    if self.check_expressions(["KR_BREAK", "TOCKAZAREZ"]):
      if not in_loop:
        return self.parse_error(curr_line)
      self.assert_leaf("KR_BREAK")
      self.assert_leaf("TOCKAZAREZ")
      return
    elif self.check_expressions(["KR_RETURN", "TOCKAZAREZ"]):
      #sto sad
      if not in_function or not function_to == [Expr("VOID")]:
        return self.parse_error(curr_line)
      self.assert_leaf("KR_RETURN")
      self.assert_leaf("TOCKAZAREZ")
    elif self.check_expressions(["KR_RETURN", "<izraz>", "TOCKAZAREZ"]): #ovaj je zanimljiv
      self.assert_leaf("KR_RETURN")
      expr = self.izraz()
      outputCode.addCommandToFunction(currFunction, 'MOVE R1, R6')
      if not in_function:
        return self.parse_error(curr_line)
      if not [expr] == function_to:
        return self.parse_error(curr_line)
      self.assert_leaf("TOCKAZAREZ")


  """PRIMARNI IZRAZ"""
def primarni_izraz(self):
    curr_line = self.lines._iter
    pprint("# primarni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      idn = self.assert_leaf("IDN")
      if self.table.contains(idn):
        return self.table.get_var(idn)
      elif self.table.is_JUST_declared(idn):
        return self.table.get_function(idn)
      else:
        return self.parse_error(curr_line)
    elif self.check_expressions(["BROJ"]):
      expr = self.assert_leaf("BROJ")
      num = int(expr)
      outputCode.addCommandToFunction(currFunction, 'MOVE {}, R1'.format(num))

      if int(expr) < -2**31 or int(expr) >= 2**31:
        return self.parse_error(curr_line)
      return Expr("INT")
    elif self.check_expressions(["ZNAK"]):
      expr = self.assert_leaf("ZNAK")
      if not len(expr) == 3 or ord(expr[1]) < 0 or ord(expr[1]) > 255:
        return self.parse_error(curr_line)
      return Expr("CHAR")
    elif self.check_expressions(["NIZ_ZNAKOVA"]):
      expr = self.assert_leaf("NIZ_ZNAKOVA")
      if not is_valid_char_array(expr):
        return self.parse_error(curr_line)
      return Expr("CHAR", is_array = True)
    elif self.check_expressions(["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]):
      self.assert_leaf("L_ZAGRADA")
      expr = self.izraz()
      self.assert_leaf("D_ZAGRADA")
      return expr
    else:
      return self.parse_error(curr_line)
      '''