from .FinalCodeGenerator import *
from .OutputCode import *
'''
ideja je da u ovom fajlu pisemo dijelove analogne onima iz FileCodeGeneratora
koji generiraju kod -> i to nece ici, bar ne baš tako, možda nam ipak trebaju
one tablice..
Ono iz jave da postoji vise fajlova, paketa i klasa nije bas tako losa praksa.
'''

outputCode = OutputCode()
currFunction = 'F_MAIN' #u koju funkciju trenutno zapisujemo naredbe


def primarni_izraz(self):

    curr_line = self.lines._iter
    pprint("# primarni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      idn = self.assert_leaf("IDN")
      if self.table.contains(idn):
          name_of_var = self.table.get_var(idn)
          # ok sad znamo da je u ovo nesto stavljeno
          return name_of_var
      elif self.table.is_JUST_declared(idn):
          # tek je deklarirano
        return self.table.get_function(idn)
      else:
        return self.parse_error(curr_line)
    elif self.check_expressions(["BROJ"]):
        # di staviti ovaj broj??
      expr = self.assert_leaf("BROJ")
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