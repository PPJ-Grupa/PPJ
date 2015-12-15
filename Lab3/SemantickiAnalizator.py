from Table import Table
from Expr import Expr
from Lines import Lines
from helpers import extract_4, is_valid_char_array

counter = 1
def pprint(stri):
  return
  global counter
  if stri[0] == "#":
    print(",," + str(counter) + " " + stri)
    counter += 1
  else:
    print(stri)

"""SEMANTICKI ANALIZATOR"""
class SemantickiAnalizator:
  """INIT"""
  def __init__(self, lines):
    self.table = Table()
    self.lines = Lines(lines)
    self.terminate = False
    return

  """CHECK EXPRESSIONS"""
  def check_expressions(self, expressions):
    if self.terminate: return False
    else: return self.lines.check_expressions(expressions)

  """ASSERT LEAF"""
  def assert_leaf(self, fst_exp, snd_exp = ""):
    global counter
    counter += 1
    if self.terminate: return False
    else: return self.lines.assert_leaf(fst_exp, snd_exp)

  """PARSE ERROR"""
  def parse_error(self):
    self.terminate = True
    return self.lines.parse_error()

  """CHECK BOTH FOR INT AND RETURN INT"""
  def check_both_for_int_and_return_int(self, fst_fun, expr, snd_fun):
    if not fst_fun().is_type("INT"):
      return self.parse_error()
    self.assert_leaf(expr)
    if not snd_fun().is_type("INT"):
      return self.parse_error()
    return Expr("INT")

  """IS SAME TYPE"""
  def is_same_type(self, fst_exp, snd_exp):
    return fst_exp.is_type("CHAR") and snd_exp.is_type("INT") \
        or (fst_exp.is_const() or snd_exp.is_const()) and fst_exp.is_type(snd_exp.get_type()) \
          and not fst_exp.is_function()

  """CAN CAST"""
  def can_cast(self, fst_exp, snd_type):
    return self.is_same_type(fst_exp, snd_exp) \
        or fst_exp.is_type("INT") and snd_exp.is_type("CHAR")

  """START"""
  def start(self):
    pprint("# Starting and checking for <prijevodna_jedinica>")
    self.check_expressions(["<prijevodna_jedinica>"])
    pprint("Calling self.prijevodna_jedinica()")
    self.prijevodna_jedinica()

######################################
############### IZRAZI ###############
######################################
  """PRIMARNI IZRAZ"""
  def primarni_izraz(self):
    pprint("# primarni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      expr = self.assert_leaf("IDN")
      if not self.table.contains(expr):
        print("AASD")
        return self.parse_error()
      else:
        return Expr(self.table.get_type(expr), lexpr = self.table.get_lexpr(expr))
    elif self.check_expressions(["BROJ"]):
      expr = self.assert_leaf("BROJ")
      if int(expr) < -2**31 or int(expr) >= 2**31:
        return self.parse_error()
      return Expr("INT", False)
    elif self.check_expressions(["ZNAK"]):
      expr = self.assert_leaf("ZNAK")
      if int(expr) < 0 or int(expr) > 255:
        return self.parse_error()
      return Expr("CHAR", 0)
    elif self.check_expressions(["NIZ_ZNAKOVA"]):
      # TODO
      raise Exception("Not fully implemented")
      expr = self.assert_leaf("NIZ_ZNAKOVA")
      if not is_valid_char_array(expr):
        return self.parse_error()
      return Expr("CHAR", is_array = True)
    elif self.check_expressions(["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]):
      self.assert_leaf("L_ZAGRADA")
      expr = self.izraz()
      self.assert_leaf("D_ZAGRADA")
      return expr
    else:
      return self.parse_error()

  """POSTFIX IZRAZI"""
  def postfiks_izraz(self):
    pprint("# postfiks_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<primarni_izraz>"]):
      return self.primarni_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]):
      expr = self.postfiks_izraz()
      if not expr.is_array():
        return self.parse_error()
      self.assert_leaf("L_UGL_ZAGRADA")
      if not self.izraz().is_type("INT"):
        return self.parse_error()
      self.assert_leaf("D_UGL_ZAGRADA")
      return Expr(expr.get_type(), lexpr = (not expr.is_const()))
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      if not expr.is_function() or not expr.is_function_from(["VOID"]):
        return self.parse_error()
      return Expr(expr.get_return_type())
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      self.assert_leaf("L_ZAGRADA")
      expr2 = self.lista_argumenata()
      self.assert_leaf("D_ZAGRADA")
      if not expr.is_function() or not expr.is_function_from(expr2.get_type()):
        return self.parse_error()
      return expr.get_return_type()
    elif self.check_expressions(["<postfiks_izraz>", "OP_INC"]):
      exp = self.postfiks_izraz()
      self.assert_leaf("OP_INC")
      if not exp.is_lexpr() or not exp.is_type("INT"):
        return self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["<postfiks_izraz>", "OP_DEC"]):
      exp = self.postfiks_izraz()
      self.assert_leaf("OP_DEC")
      if not exp.is_lexpr() or not exp.is_type("INT"):
        return self.parse_error()
      else:
        return Expr("INT", False)
    else:
      return self.parse_error()

  """LISTA ARGUMENATA"""
  def lista_argumenata(self):
    pprint("# lista_argumenata")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return [self.izraz_pridruzivanja()]
    elif self.check_expressions(["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]):
      expr = self.lista_argumenata()
      self.assert_leaf("ZAREZ")
      return expr.append(self.izraz_pridruzivanja())
    else:
      return self.parse_error()

  """UNARNI IZRAZ"""
  def unarni_izraz(self):
    pprint("# unarni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<postfiks_izraz>"]):
      return self.postfiks_izraz()
    elif self.check_expressions(["OP_DEC", "<unarni_izraz>"]):
      self.assert_leaf("OP_DEC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr() or not expr.is_type("INT"):
        return self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["OP_INC", "<unarni_izraz>"]):
      self.assert_leaf("OP_INC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr() or not expr.is_type("INT"):
        return self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["<unarni_operator>", "<cast_izraz>"]):
      expr = self.cast_izraz()
      if not expr.is_type("INT"):
        return self.parse_error()
      else:
        return Expr("INT", False)
    else:
      return self.parse_error()

  """UNARNI OPERATOR"""
  def unarni_operator(self):
    pprint("# unarni_operator")
    pprint(self.lines.get_line())

    if self.check_expressions(["PLUS"]):
      self.assert_leaf("PLUS")
      return
    elif self.check_expressions(["MINUS"]):
      self.assert_leaf("MINUS")
      return
    elif self.check_expressions(["OP_TILDA"]):
      self.assert_leaf("OP_TILDA")
      return
    elif sself.check_expressions(["OP_NEG"]):
      self.assert_leaf("OP_NEG")
      return
    else:
      return self.parse_error()

  """CAST IZRAZ"""
  def cast_izraz(self):
    pprint("# cast_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<unarni_izraz>"]):
      return self.unarni_izraz()
    elif self.check_expressions(["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]):
      self.assert_leaf("L_ZAGRADA")
      expr = self.ime_tipa()
      self.assert_leaf("D_ZAGRADA")
      expr2 = self.cast_izraz()
      if not self.can_cast(expr.get_type(), expr2.get_type()):
        return self.parse_error()
      else:
        return Expr(expr.get_type(), False)

  """IME TIPA"""
  def ime_tipa(self):
    pprint("# ime_tipa")
    pprint(self.lines.get_line())

    if self.check_expressions(["<specifikator_tipa>"]):
      return self.specifikator_tipa()
    elif self.check_expressions(["KR_CONST", "<specifikator_tipa>"]):
      self.assert_leaf("KR_CONST")
      expr = self.specifikator_tipa()
      if expr.is_type("VOID"):
        return self.parse_error()
      else:
        return Expr(expr.get_type(), is_const = True)
    else:
      return self.parse_error()

  """SPECIFIKATOR TIPA"""
  def specifikator_tipa(self):
    pprint("# specifikator_tipa")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_VOID"]):
      self.assert_leaf("KR_VOID", "void")
      return Expr("VOID", False)
    elif self.check_expressions(["KR_CHAR"]):
      self.assert_leaf("KR_CHAR", "char")
      return Expr("CHAR", False)
    elif self.check_expressions(["KR_INT"]):
      self.assert_leaf("KR_INT", "int")
      return Expr("INT", False)
    else:
      return self.parse_error()

  """MULTIPLIKATIVNI IZRAZ"""
  def multiplikativni_izraz(self):
    pprint("# multiplikativni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<cast_izraz>"]):
      return self.cast_izraz()
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_PUTA", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_PUTA", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_DIJELI", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_DIJELI", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_MOD", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_MOD", self.cast_izraz)
    else:
      return self.parse_error()

  """ADITIVNI IZRAZ"""
  def aditivni_izraz(self):
    pprint("# aditivni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<multiplikativni_izraz>"]):
      return self.multiplikativni_izraz()
    elif self.check_expressions(["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.aditivni_izraz, "PLUS", self.multiplikativni_izraz)
    elif self.check_expressions(["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.aditivni_izraz, "MINUS", self.multiplikativni_izraz)
    else:
      return self.parse_error()

  """ODNOSNI IZRAZ"""
  def odnosni_izraz(self):
    pprint("# odnosni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<aditivni_izraz>"]):
      return self.aditivni_izraz()
    elif self.check_expressions(["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.odnosni_izraz, "OP_LT" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.odnosni_izraz, "OP_GT" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.odnosni_izraz, "OP_LTE" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.odnosni_izraz, "OP_GTE" , self.aditivni_izraz)
    else:
      return self.parse_error()

  """JEDNAKOSNI IZRAZ"""
  def jednakosni_izraz(self):
    pprint("# jednakosni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<odnosni_izraz>"]):
      return self.odnosni_izraz()
    elif self.check_expressions(["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.jednakosni_izraz, "OP_EQ", self.odnosni_izraz)
    elif self.check_expressions(["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.jednakosni_izraz, "OP_NEQ", self.odnosni_izraz)
    else:
      return self.parse_error()

  """BIN I IZRAZ"""
  def bin_i_izraz(self):
    pprint("# bin_i_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<jednakosni_izraz>"]):
      return self.jednakosni_izraz()
    elif self.check_expressions(["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_i_izraz, "OP_BIN_I", self.jednakosni_izraz)
    else:
      return self.parse_error()

  """BIN XILI IZRAZ"""
  def bin_xili_izraz(self):
    pprint("# bin_xili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_i_izraz>"]):
      return self.bin_i_izraz()
    elif self.check_expressions(["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_xili_izraz, "OP_BIN_XILI", self.bin_i_izraz)
    else:
      return self.parse_error()

  """BIN ILI IZRAZ"""
  def bin_ili_izraz(self):
    pprint("# bin_ili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_xili_izraz>"]):
      return self.bin_xili_izraz()
    elif self.check_expressions(["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_ili_izraz, "OP_BIN_ILI", self.bin_xili_izraz)
    else:
      return self.parse_error()

  """LOG I IZRAZ"""
  def log_i_izraz(self):
    pprint("# log_i_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_ili_izraz>"]):
      return self.bin_ili_izraz()
    elif self.check_expressions(["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]):
      return self.check_both_for_int_and_return_int(self.log_i_izraz, "OP_I", self.bin_xili_izraz)
    else:
      return self.parse_error()

  """LOG ILI IZRAZ"""
  def log_ili_izraz(self):
    pprint("# log_ili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<log_i_izraz>"]):
      return self.log_i_izraz()
    elif self.check_expressions(["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]):
      return self.check_both_for_int_and_return_int(self.log_ili_izraz, "OP_ILI", self.log_i_izraz)
    else:
      return self.parse_error()

  """IZRAZ PRIDRUZIVANJA"""
  def izraz_pridruzivanja(self):
    pprint("# izraz_pridruzivanja")
    pprint(self.lines.get_line())

    if self.check_expressions(["<log_ili_izraz>"]):
      return self.log_ili_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]):
      expr = self.postfiks_izraz()
      if not expr.is_lexpr():
        return self.parse_error()
      self.assert_leaf("OP_PRIDRUZI")
      expr2 = self.izraz_pridruzivanja()
      if not expr.is_type(expr2.get_type()):
        return self.parse_error()
      return Expr(expr.get_type())
    else:
      return self.parse_error()

  """IZRAZ"""
  def izraz(self):
    pprint("# izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return self.izraz_pridruzivanja()
    elif self.check_expressions(["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]):
      self.izraz()
      self.assert_leaf("ZAREZ")
      return Expr(izraz_pridruzivanja().get_type())


##################################
## NAREDBENA STRUKTURA PROGRAMA ##
##################################

  """SLOZENA NAREDBA"""
  def slozena_naredba(self, in_loop = False, in_function = False, function_to = []):
    pprint("# slozena_naredba")
    pprint(self.lines.get_line())

    if self.check_expressions(["L_VIT_ZAGRADA", "<lista_naredbi>", "D_VIT_ZAGRADA"]):
      self.assert_leaf("L_VIT_ZAGRADA")
      self.lista_naredbi(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.assert_leaf("D_VIT_ZAGRADA")
    elif self.check_expressions(["L_VIT_ZAGRADA", "<lista_deklaracija>", "<lista_naredbi>"
                               , "D_VIT_ZAGRADA"]):
      self.assert_leaf("L_VIT_ZAGRADA")
      self.lista_deklaracija()
      self.lista_naredbi(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.assert_leaf("D_VIT_ZAGRADA")
    else:
      return self.parse_error()

  """LISTA NAREDBI"""
  def lista_naredbi(self, in_loop = False, in_function = False, function_to = []):
    pprint("# lista_naredbi")
    pprint(self.lines.get_line())

    if self.check_expressions(["<naredba>"]):
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["<lista_naredbi>", "<naredba>"]):
      self.lista_naredbi(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error()

  """NAREDBA"""
  def naredba(self, in_loop = False, in_function = False, function_to = []):
    pprint("# naredba")
    pprint(self.lines.get_line())

    if self.check_expressions(["<slozena_naredba>"]):
      self.slozena_naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["<izraz_naredba>"]):
      self.izraz_naredba()
    elif self.check_expressions(["<naredba_grananja>"]):
      self.naredba_grananja(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["<naredba_petlje>"]):
      self.naredba_petlje(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["<naredba_skoka>"]):
      self.naredba_skoka(in_loop = in_loop, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error()

  """IZRAZ NAREDBA"""
  def izraz_naredba(self):
    pprint("# izraz_naredba")
    pprint(self.lines.get_line())

    if self.check_expressions(["TOCKAZAREZ"]):
      self.assert_leaf("TOCKAZAREZ")
      return Expr("INT")
    elif self.check_expressions(["<izraz>", "TOCKAZAREZ"]):
      expr = self.izraz()
      self.assert_leaf("TOCKAZAREZ")
      return Expr(expr.get_type())
    else:
      return self.parse_error()

  """NAREDBA GRANANJA"""
  def naredba_grananja(self, in_loop = False, in_function = False, function_to = []):
    pprint("# naredba_grananja")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_IF")
      self.assert_leaf("L_ZAGRADA")
      expr = self.izraz()
      pprint(expr.get_type())
      if not expr.is_type("INT"):
        return self.parse_error()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>"
                                ,"D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]):
      self.assert_leaf("KR_IF")
      self.assert_leaf("L_ZAGRADA")
      if not self.izraz().is_type("INT"):
        return self.parse_error()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.assert_leaf("KR_ELSE")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error()

  """NAREDBA PETLJE"""
  def naredba_petlje(self, in_loop = False, in_function = False, function_to = []):
    pprint("# naredba_petlje")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_WHILE")
      self.assert_leaf("L_ZAGRADA")
      if not self.izraz().is_type("INT"):
        return self.parse_error()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_FOR")
      self.assert_leaf("L_ZAGRADA")
      self.izraz_naredba()
      if not self.izraz_naredba().is_type("INT"):
        return self.parse_error()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_FOR")
      self.assert_leaf("L_ZAGRADA")
      self.izraz_naredba()
      if not self.izraz_naredba().is_type("INT"):
        return self.parse_error()
      self.izraz()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error()

  """NAREDBA SKOKA"""
  def naredba_skoka(self, in_loop = False, in_function = False, function_to = []):
    pprint("# naredba_skoka")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_CONTINUE", "TOCKAZAREZ"]):
      if not in_loop:
        self.parse_error()
      self.assert_leaf("KR_CONTINUE")
      self.assert_leaf("TOCKAZAREZ")
      return
    if self.check_expressions(["KR_BREAK", "TOCKAZAREZ"]):
      if not in_loop:
        self.parse_error()
      self.assert_leaf("KR_BREAK")
      self.assert_leaf("TOCKAZAREZ")
      return
    elif self.check_expressions(["KR_RETURN", "TOCKAZAREZ"]):
      if not in_function or not function_to == "VOID":
        self.parse_error()
      self.assert_leaf("KR_RETURN")
      self.assert_leaf("TOCKAZAREZ")
      return
    elif self.check_expressions(["KR_RETURN", "<izraz>", "TOCKAZAREZ"]):
      self.assert_leaf("KR_RETURN")
      expr = self.izraz()
      if not in_function or not expr.is_type(function_to):
        self.parse_error()
      self.assert_leaf("TOCKAZAREZ")
      return

  """PRIJEVODNA JEDINICA"""
  def prijevodna_jedinica(self):
    pprint("# prijevodna_jedinica")
    pprint(self.lines.get_line())

    if self.check_expressions(["<vanjska_deklaracija>"]):
      pprint("<vanjska_deklaracija>")
      self.vanjska_deklaracija()
    elif self.check_expressions(["<prijevodna_jedinica>", "<vanjska_deklaracija>"]):
      pprint("<prijevodna_jedinica> <vanjska_deklaracija>")
      self.prijevodna_jedinica()
      self.vanjska_deklaracija()
    else:
      return self.parse_error()

  """VANJSKA DEKLARACIJA"""
  def vanjska_deklaracija(self):
    pprint("# vanjska_deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<definicija_funkcije>"]):
      self.definicija_funkcije()
    elif self.check_expressions(["<deklaracija>"]):
      self.deklaracija()
    else:
      return self.parse_error()

##############################
## DEKLARACIJE I DEFINICIJE ##
##############################

  """DEFINICIJA FUNKCIJE"""
  def definicija_funkcije(self):
    pprint("# definicija_funkcije")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"
                             , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const():
        return self.parse_error()
      idn = self.assert_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        return self.parse_error()
      ## 4
      if self.table.is_declared(idn, ["VOID"], expr.get_type()):
        return self.parse_error()
      ## 5
      if not self.table.is_declared(idn, ["VOID"], expr.get_type()):
        self.table.declare(idn, ["VOID"], expr.get_type())
      if not self.table.is_defined(idn, ["VOID"], expr.get_type()):
        self.table.define(idn, ["VOID"], expr.get_type())
      ## X
      self.assert_leaf("L_ZAGRADA")
      self.assert_leaf("KR_VOID")
      self.assert_leaf("D_ZAGRADA")
      ## 6
      self.slozena_naredba(in_function = True, function_to = expr.get_type())
    elif self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"
                               , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const():
        return self.parse_error()
      idn = self.assert_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        return self.parse_error()
      ## X
      self.assert_leaf("L_ZAGRADA")
      ## 4
      expr2 = lista_parametara()
      ## 5
      if self.table.is_declared(idn) and \
          not (self.table.is_function_from(idn, expr2.get_type()) \
            and self.table.is_function_to(idn, expr.get_type())):
        return self.parse_error()
      ## 6
      if not self.table.is_declared(idn, expr2.get_type(), expr.get_type()):
        self.table.declare(idn, expr2.get_type(), expr.get_type())
      if not self.table.is_defined(idn, expr2.get_type(), expr.get_type()):
        self.table.define(idn, expr2.get_type(), expr.get_type())
      ## X
      self.assert_leaf("D_ZAGRADA")
      ## 7 !!! Careful about function parameters. Should be implemented (i think)
      self.slozena_naredba(in_function = True, function_to = expr.get_type())
    else:
      return self.parse_error()

  """LISTA PARAMETARA"""
  def lista_parametara(self):
    pprint("# lista_parametara")
    pprint(self.lines.get_line())

    if self.check_expressions(["<deklaracija_parametra>"]):
      return deklaracija_parametra()
    elif self.check_expressions(["<lista_parametara>", "ZAREZ", "<deklaracija_parametra>"]):
      tipovi, imena = lista_parametara()
      self.assert_leaf("ZAREZ")
      tip, ime = deklaracija_parametra()
      return tipovi.append(tip), imena.append(ime)
    else:
      return self.parse_error()

  """DEKLARACIJA PARAMETRA"""
  def deklaracija_parametra(self):
    pprint("# deklaracija_parametra")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN"]):
      raise Exception("Not yet implemented")
      expr = ime_tipa()
      if expr.is_type("VOID"):
        return self.parse_error()
      return expr.get_type(), assert_leaf("IDN")
    elif self.check_expressions(["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"]):
      raise Exception("Not yet implemented")
      expr = ime_tipa()
      if expr.is_type("VOID"):
        return self.parse_error()
      return Expr(expr.get_type(), is_array = True)

  """LISTA DEKLARACIJA"""
  def lista_deklaracija(self):
    pprint("# lista_deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<deklaracija>"]):
      self.deklaracija()
    elif self.check_expressions(["<lista_deklaracija>", "<deklaracija>"]):
      self.lista_deklaracija()
      self.deklaracija()
    else:
      return self.parse_error()

  def deklaracija(self):
    pprint("# deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "<lista_init_deklaratora>", "TOCKAZAREZ"]):
      raise Exception("Not implemented")
      expr = self.ime_tipa()
      expr2 = self.lista_init_deklaratora()
      return

  def lista_init_deklaratora(self):
    pprint("# lista_init_deklaratora")
    pprint(self.lines.get_line())

    if self.check_expressions(["<init_deklarator>"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["<lista_init_deklaratora>", "ZAREZ", "<init_deklarator>"]):
      raise Exception("Not implemented")
    else:
      return self.parse_error()

  def init_deklarator(self):
    pprint("# init_deklarator")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izravni_deklarator>"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["<izravni_deklarator>", "OP_PRIDRUZI", "<inicijalizator>"]):
      raise Exception("Not implemented")
    else:
      return self.parse_error()

  def izravni_deklarator(self):
    pprint("# izravni_deklarator")
    pprint(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["IDN", "L_UGL_ZAGRADA", "BROJ", "D_UGL_ZAGRADA"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"]):
      raise Exception("Not implemented")
    else:
      return self.parse_error()

  def inicijalizator(self):
    pprint("# inicijalizator")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["L_VIT_ZAGRADA", "<lista_izraza_pridruzivanja>", "D_VIT_ZAGRADA"]):
      raise Exception("Not implemented")
    else:
      return self.parse_error()

  def lista_izraza_pridruzivanja(self):
    pprint("# lista_izraza_pridruzivanja")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      raise Exception("Not implemented")
    elif self.check_expressions(["<lista_izraza_pridruzivanja>", "ZAREZ", "<izraz_pridruzivanja>"]):
      raise Exception("Not implemented")
    else:
      return self.parse_error()

