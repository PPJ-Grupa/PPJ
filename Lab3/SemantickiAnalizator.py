from Table import Table
from Expr import Expr
from Lines import Lines
from helpers import is_valid_char_array

counter = 1
def pprint(stri):
  #return
  global counter
  if type(stri) is str and stri[0] == "#":
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
  def parse_error(self, curr_line):
    self.terminate = True
    return self.lines.parse_error(curr_line)

  """CHECK BOTH FOR INT AND RETURN INT"""
  def check_both_for_int_and_return_int(self, curr_line, fst_fun, expr, snd_fun):
    if not fst_fun() == Expr("INT"):
      return self.parse_error(curr_line)
    self.assert_leaf(expr)
    if not snd_fun() == Expr("INT"):
      return self.parse_error(curr_line)
    return Expr("INT")

  """CAN CAST"""
  def can_cast(self, fst_exp, snd_exp):
    return fst_exp == snd_exp \
        or fst_exp == Expr("INT") and snd_exp == Expr("CHAR")

  """POST TRAVERSAL CHECKS"""
  def post_traversal_checks(self):
    if not "main" in self.table._declared_functions \
        or not "main" in self.table._defined_functions \
        or not self.table._defined_functions["main"] == \
            self.table._declared_functions["main"] \
        or not self.table._defined_functions["main"]._function_from_types == \
            [Expr("VOID")] \
        or not self.table._defined_functions["main"]._function_to_types[0]._type == "INT":
      print("main")
      return True

    for fun in self.table._declared_functions:
      if not fun in self.table._defined_functions:
        print("function")
        return True
    return False

  """START"""
  def start(self):
    #pprint("# Starting and checking for <prijevodna_jedinica>")
    self.check_expressions(["<prijevodna_jedinica>"])
    #pprint("Calling self.prijevodna_jedinica()")
    self.prijevodna_jedinica()

    if not self.terminate:
      if not self.post_traversal_checks():
        pprint("Succesful semantic analysis. No errors!")
      else:
        pprint("Post traversal errors found!")

######################################
############### IZRAZI ###############
######################################
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

  """POSTFIX IZRAZ"""
  def postfiks_izraz(self):
    curr_line = self.lines._iter
    pprint("# postfiks_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]):
      expr = self.postfiks_izraz()
      _expr = Expr(expr)
      if not _expr.is_array:
        return self.parse_error(curr_line)
      ## We are accessing an element of this array so the return type is not array
      _expr.is_array = False
      self.assert_leaf("L_UGL_ZAGRADA")
      if not self.izraz() == Expr("INT"):
        return self.parse_error(curr_line)
      self.assert_leaf("D_UGL_ZAGRADA")
      if _expr.is_const:
        return _expr
      else:
        return _expr.set_to_lexpr()
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      self.assert_leaf("L_ZAGRADA")
      self.assert_leaf("D_ZAGRADA")
      if not expr.is_function or not expr.is_function_from([Expr("VOID")]):
        return self.parse_error(curr_line)
      ret = expr.get_return_type()
      if len(ret) != 1:
        raise Exception("This should not happen")
      else:
        return ret[0]
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      self.assert_leaf("L_ZAGRADA")
      expr2 = self.lista_argumenata()
      self.assert_leaf("D_ZAGRADA")
      if not expr.is_function or not expr.is_function_from(expr2):
        return self.parse_error(curr_line)
      ret = expr.get_return_type()
      if len(ret) != 1:
        raise Exception("This should not happen")
      else:
        return ret[0]
    elif self.check_expressions(["<postfiks_izraz>", "OP_INC"]):
      expr = self.postfiks_izraz()
      self.assert_leaf("OP_INC")
      if not expr.is_lexpr or not expr == Expr("INT"):
        return self.parse_error(curr_line)
      else:
        return Expr("INT")
    elif self.check_expressions(["<postfiks_izraz>", "OP_DEC"]):
      expr = self.postfiks_izraz()
      self.assert_leaf("OP_DEC")
      if not expr.is_lexpr or not expr == Expr("INT"):
        return self.parse_error(curr_line)
      else:
        return Expr("INT")
    elif self.check_expressions(["<primarni_izraz>"]):
      return self.primarni_izraz()
    else:
      return self.parse_error(curr_line)

  """LISTA ARGUMENATA"""
  def lista_argumenata(self):
    curr_line = self.lines._iter
    pprint("# lista_argumenata")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      expr = self.izraz_pridruzivanja()
      return [expr]
    elif self.check_expressions(["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]):
      expr = self.lista_argumenata()
      self.assert_leaf("ZAREZ")
      expr2 = self.izraz_pridruzivanja()
      return expr + [expr2]
    else:
      return self.parse_error(curr_line)

  """UNARNI IZRAZ"""
  def unarni_izraz(self):
    curr_line = self.lines._iter
    pprint("# unarni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<postfiks_izraz>"]):
      return self.postfiks_izraz()
    elif self.check_expressions(["OP_DEC", "<unarni_izraz>"]):
      self.assert_leaf("OP_DEC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr or not expr == Expr("INT"):
        return self.parse_error(curr_line)
      else:
        return Expr("INT")
    elif self.check_expressions(["OP_INC", "<unarni_izraz>"]):
      self.assert_leaf("OP_INC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr or not expr == Expr("INT"):
        return self.parse_error(curr_line)
      else:
        return Expr("INT")
    elif self.check_expressions(["<unarni_operator>", "<cast_izraz>"]):
      self.unarni_operator()
      expr = self.cast_izraz()
      if not expr == Expr("INT"):
        return self.parse_error(curr_line)
      else:
        return Expr("INT")
    else:
      return self.parse_error(curr_line)

  """UNARNI OPERATOR"""
  def unarni_operator(self):
    curr_line = self.lines._iter
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
    elif self.check_expressions(["OP_NEG"]):
      self.assert_leaf("OP_NEG")
      return
    else:
      return self.parse_error(curr_line)

  """CAST IZRAZ"""
  def cast_izraz(self):
    curr_line = self.lines._iter
    pprint("# cast_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<unarni_izraz>"]):
      return self.unarni_izraz()
    elif self.check_expressions(["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]):
      self.assert_leaf("L_ZAGRADA")
      expr = self.ime_tipa()
      self.assert_leaf("D_ZAGRADA")
      expr2 = self.cast_izraz()
      if not self.can_cast(expr, expr2):
        return self.parse_error(curr_line)
      else:
        return expr

  """IME TIPA"""
  def ime_tipa(self):
    curr_line = self.lines._iter
    pprint("# ime_tipa")
    pprint(self.lines.get_line())

    if self.check_expressions(["<specifikator_tipa>"]):
      return self.specifikator_tipa()
    elif self.check_expressions(["KR_CONST", "<specifikator_tipa>"]):
      self.assert_leaf("KR_CONST")
      expr = self.specifikator_tipa()
      if expr == Expr("VOID"):
        return self.parse_error(curr_line)
      else:
        return expr.set_to_const()
    else:
      return self.parse_error(curr_line)

  """SPECIFIKATOR TIPA"""
  def specifikator_tipa(self):
    curr_line = self.lines._iter
    pprint("# specifikator_tipa")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_VOID"]):
      self.assert_leaf("KR_VOID", "void")
      return Expr("VOID")
    elif self.check_expressions(["KR_CHAR"]):
      self.assert_leaf("KR_CHAR", "char")
      return Expr("CHAR")
    elif self.check_expressions(["KR_INT"]):
      self.assert_leaf("KR_INT", "int")
      return Expr("INT")
    else:
      return self.parse_error(curr_line)

  """MULTIPLIKATIVNI IZRAZ"""
  def multiplikativni_izraz(self):
    curr_line = self.lines._iter
    pprint("# multiplikativni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<cast_izraz>"]):
      return self.cast_izraz()
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_PUTA", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.multiplikativni_izraz, "OP_PUTA", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_DIJELI", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.multiplikativni_izraz, "OP_DIJELI", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_MOD", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.multiplikativni_izraz, "OP_MOD", self.cast_izraz)
    else:
      return self.parse_error(curr_line)

  """ADITIVNI IZRAZ"""
  def aditivni_izraz(self):
    curr_line = self.lines._iter
    pprint("# aditivni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<multiplikativni_izraz>"]):
      return self.multiplikativni_izraz()
    elif self.check_expressions(["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.aditivni_izraz, "PLUS", self.multiplikativni_izraz)
    elif self.check_expressions(["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.aditivni_izraz, "MINUS", self.multiplikativni_izraz)
    else:
      return self.parse_error(curr_line)

  """ODNOSNI IZRAZ"""
  def odnosni_izraz(self):
    curr_line = self.lines._iter
    pprint("# odnosni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<aditivni_izraz>"]):
      return self.aditivni_izraz()
    elif self.check_expressions(["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.odnosni_izraz, "OP_LT" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.odnosni_izraz, "OP_GT" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.odnosni_izraz, "OP_LTE" , self.aditivni_izraz)
    elif self.check_expressions(["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.odnosni_izraz, "OP_GTE" , self.aditivni_izraz)
    else:
      return self.parse_error(curr_line)

  """JEDNAKOSNI IZRAZ"""
  def jednakosni_izraz(self):
    curr_line = self.lines._iter
    pprint("# jednakosni_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<odnosni_izraz>"]):
      return self.odnosni_izraz()
    elif self.check_expressions(["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.jednakosni_izraz, "OP_EQ", self.odnosni_izraz)
    elif self.check_expressions(["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.jednakosni_izraz, "OP_NEQ", self.odnosni_izraz)
    else:
      return self.parse_error(curr_line)

  """BIN I IZRAZ"""
  def bin_i_izraz(self):
    curr_line = self.lines._iter
    pprint("# bin_i_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<jednakosni_izraz>"]):
      return self.jednakosni_izraz()
    elif self.check_expressions(["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.bin_i_izraz, "OP_BIN_I", self.jednakosni_izraz)
    else:
      return self.parse_error(curr_line)

  """BIN XILI IZRAZ"""
  def bin_xili_izraz(self):
    curr_line = self.lines._iter
    pprint("# bin_xili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_i_izraz>"]):
      return self.bin_i_izraz()
    elif self.check_expressions(["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.bin_xili_izraz, "OP_BIN_XILI", self.bin_i_izraz)
    else:
      return self.parse_error(curr_line)

  """BIN ILI IZRAZ"""
  def bin_ili_izraz(self):
    curr_line = self.lines._iter
    pprint("# bin_ili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_xili_izraz>"]):
      return self.bin_xili_izraz()
    elif self.check_expressions(["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.bin_ili_izraz, "OP_BIN_ILI", self.bin_xili_izraz)
    else:
      return self.parse_error(curr_line)

  """LOG I IZRAZ"""
  def log_i_izraz(self):
    curr_line = self.lines._iter
    pprint("# log_i_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<bin_ili_izraz>"]):
      return self.bin_ili_izraz()
    elif self.check_expressions(["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.log_i_izraz, "OP_I", self.bin_ili_izraz)
    else:
      return self.parse_error(curr_line)

  """LOG ILI IZRAZ"""
  def log_ili_izraz(self):
    curr_line = self.lines._iter
    pprint("# log_ili_izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<log_i_izraz>"]):
      return self.log_i_izraz()
    elif self.check_expressions(["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]):
      return self.check_both_for_int_and_return_int(curr_line, self.log_ili_izraz, "OP_ILI", self.log_i_izraz)
    else:
      return self.parse_error(curr_line)

  """IZRAZ PRIDRUZIVANJA"""
  def izraz_pridruzivanja(self):
    curr_line = self.lines._iter
    pprint("# izraz_pridruzivanja")
    pprint(self.lines.get_line())

    if self.check_expressions(["<log_ili_izraz>"]):
      return self.log_ili_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]):
      expr = self.postfiks_izraz()
      if not expr.is_lexpr:
        return self.parse_error(curr_line)
      self.assert_leaf("OP_PRIDRUZI")
      expr2 = self.izraz_pridruzivanja()
      if not expr == expr2:
        return self.parse_error(curr_line)
      return expr
    else:
      return self.parse_error(curr_line)

  """IZRAZ"""
  def izraz(self):
    curr_line = self.lines._iter
    pprint("# izraz")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return self.izraz_pridruzivanja()
    elif self.check_expressions(["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]):
      self.izraz()
      self.assert_leaf("ZAREZ")
      return izraz_pridruzivanja()


##################################
## NAREDBENA STRUKTURA PROGRAMA ##
##################################

  """SLOZENA NAREDBA"""
  def slozena_naredba(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
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
      return self.parse_error(curr_line)

  """LISTA NAREDBI"""
  def lista_naredbi(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
    pprint("# lista_naredbi")
    pprint(self.lines.get_line())

    if self.check_expressions(["<naredba>"]):
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["<lista_naredbi>", "<naredba>"]):
      self.lista_naredbi(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error(curr_line)

  """NAREDBA"""
  def naredba(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
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
      return self.parse_error(curr_line)

  """IZRAZ NAREDBA"""
  def izraz_naredba(self):
    curr_line = self.lines._iter
    pprint("# izraz_naredba")
    pprint(self.lines.get_line())

    if self.check_expressions(["TOCKAZAREZ"]):
      self.assert_leaf("TOCKAZAREZ")
      return Expr("INT")
    elif self.check_expressions(["<izraz>", "TOCKAZAREZ"]):
      expr = self.izraz()
      self.assert_leaf("TOCKAZAREZ")
      return expr
    else:
      return self.parse_error(curr_line)

  """NAREDBA GRANANJA"""
  def naredba_grananja(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
    pprint("# naredba_grananja")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_IF")
      self.assert_leaf("L_ZAGRADA")
      expr = self.izraz()
      if not expr == Expr("INT"):
        return self.parse_error(curr_line)
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>"
                                ,"D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]):
      self.assert_leaf("KR_IF")
      self.assert_leaf("L_ZAGRADA")
      if not self.izraz() == Expr("INT"):
        return self.parse_error(curr_line)
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
      self.assert_leaf("KR_ELSE")
      self.naredba(in_loop = in_loop, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error(curr_line)

  """NAREDBA PETLJE"""
  def naredba_petlje(self, in_loop = False, in_function = False, function_to = []):
    curr_line = self.lines._iter
    pprint("# naredba_petlje")
    pprint(self.lines.get_line())

    if self.check_expressions(["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_WHILE")
      self.assert_leaf("L_ZAGRADA")
      if not self.izraz() == Expr("INT"):
        return self.parse_error(curr_line)
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_FOR")
      self.assert_leaf("L_ZAGRADA")
      self.izraz_naredba()
      if not self.izraz_naredba() == Expr("INT"):
        return self.parse_error(curr_line)
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"<izraz>", "D_ZAGRADA", "<naredba>"]):
      self.assert_leaf("KR_FOR")
      self.assert_leaf("L_ZAGRADA")
      self.izraz_naredba()
      if not self.izraz_naredba() == Expr("INT"):
        return self.parse_error(curr_line)
      self.izraz()
      self.assert_leaf("D_ZAGRADA")
      self.naredba(in_loop = True, in_function = in_function, function_to = function_to)
    else:
      return self.parse_error(curr_line)

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
      if not in_function or not function_to == [Expr("VOID")]:
        return self.parse_error(curr_line)
      self.assert_leaf("KR_RETURN")
      self.assert_leaf("TOCKAZAREZ")
    elif self.check_expressions(["KR_RETURN", "<izraz>", "TOCKAZAREZ"]):
      self.assert_leaf("KR_RETURN")
      expr = self.izraz()
      if not in_function:
        return self.parse_error(curr_line)
      if not [expr] == function_to:
        return self.parse_error(curr_line)
      self.assert_leaf("TOCKAZAREZ")

  """PRIJEVODNA JEDINICA"""
  def prijevodna_jedinica(self):
    curr_line = self.lines._iter
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
      return self.parse_error(curr_line)

  """VANJSKA DEKLARACIJA"""
  def vanjska_deklaracija(self):
    curr_line = self.lines._iter
    pprint("# vanjska_deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<definicija_funkcije>"]):
      self.definicija_funkcije()
    elif self.check_expressions(["<deklaracija>"]):
      pprint("# vanjska_deklaracija")
      self.deklaracija()
    else:
      return self.parse_error(curr_line)

##############################
## DEKLARACIJE I DEFINICIJE ##
##############################

  """DEFINICIJA FUNKCIJE"""
  def definicija_funkcije(self):
    curr_line = self.lines._iter
    pprint("# definicija_funkcije")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"
                             , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const:
        return self.parse_error(curr_line)
      idn = self.assert_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        return self.parse_error(curr_line)
      ## 4
      if self.table.is_declared(idn, [Expr("VOID")], [expr]):
        return self.parse_error(curr_line)
      ## 5
      if not self.table.is_declared(idn, [Expr("VOID")], [expr]):
        self.table.declare_fun(idn, [Expr("VOID")], [expr])
      if not self.table.is_defined(idn, [Expr("VOID")], [expr]):
        self.table.define(idn, [Expr("VOID")], [expr])
      ## X
      self.assert_leaf("L_ZAGRADA")
      self.assert_leaf("KR_VOID")
      self.assert_leaf("D_ZAGRADA")
      ## 6
      self.slozena_naredba(in_function = True, function_to = [expr])
    elif self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"
                               , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const:
        return self.parse_error(curr_line)
      idn = self.assert_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        return self.parse_error(curr_line)
      ## X
      self.assert_leaf("L_ZAGRADA")
      ## 4
      types, names = self.lista_parametara()
      ## 4 . continued
      ### Addomg types+names to scope (no scoping implemented yet)
      for i, name in enumerate(names):
        self.table.declare_var(name, types[i])
      ## 5
      if self.table.is_declared(idn, types, [expr]):
        return self.parse_error(curr_line)
      ## 6
      if not self.table.is_declared(idn, types, [expr]):
        self.table.declare_fun(idn, types, [expr])
      if not self.table.is_defined(idn, types, [expr]):
        self.table.define(idn, types, [expr])
      ## X
      self.assert_leaf("D_ZAGRADA")
      ## 7 !!! Careful about function parameters. Should be implemented (i think)
      pprint("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      pprint(expr)
      self.slozena_naredba(in_function = True, function_to = [expr])
    else:
      return self.parse_error(curr_line)

  """LISTA PARAMETARA"""
  def lista_parametara(self):
    curr_line = self.lines._iter
    pprint("# lista_parametara")
    pprint(self.lines.get_line())

    if self.check_expressions(["<deklaracija_parametra>"]):
      tip, ime = self.deklaracija_parametra()
      return [tip], [ime]
    elif self.check_expressions(["<lista_parametara>", "ZAREZ", "<deklaracija_parametra>"]):
      tipovi, imena = self.lista_parametara()
      self.assert_leaf("ZAREZ")
      tip, ime = self.deklaracija_parametra()
      return tipovi + [tip], imena + [ime]
    else:
      return self.parse_error(curr_line)

  """DEKLARACIJA PARAMETRA"""
  def deklaracija_parametra(self):
    curr_line = self.lines._iter
    pprint("# deklaracija_parametra")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"]):
      expr = self.ime_tipa()
      if expr == Expr("VOID"):
        return self.parse_error(curr_line)
      idn =  self.assert_leaf("IDN")
      self.assert_leaf("L_UGL_ZAGRADA")
      self.assert_leaf("D_UGL_ZAGRADA")
      return expr.set_to_array(), idn
    elif self.check_expressions(["<ime_tipa>", "IDN"]):
      expr = self.ime_tipa()
      if expr == Expr("VOID"):
        return self.parse_error(curr_line)
      idn = self.assert_leaf("IDN")
      return expr, idn
    else:
      return self.parse_error(curr_line)

  """LISTA DEKLARACIJA"""
  def lista_deklaracija(self):
    curr_line = self.lines._iter
    pprint("# lista_deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<deklaracija>"]):
      self.deklaracija()
    elif self.check_expressions(["<lista_deklaracija>", "<deklaracija>"]):
      self.lista_deklaracija()
      self.deklaracija()
    else:
      return self.parse_error(curr_line)

  """DEKLRACIJA"""
  def deklaracija(self):
    curr_line = self.lines._iter
    pprint("# deklaracija")
    pprint(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "<lista_init_deklaratora>", "TOCKAZAREZ"]):
      expr = self.ime_tipa()
      self.lista_init_deklaratora(expr)
      self.assert_leaf("TOCKAZAREZ")
      return

  """LISTA INIT DEKLARATORA"""
  def lista_init_deklaratora(self, inherited_type):
    curr_line = self.lines._iter
    pprint("# lista_init_deklaratora")
    pprint(self.lines.get_line())

    if self.check_expressions(["<init_deklarator>"]):
      self.init_deklarator(inherited_type)
    elif self.check_expressions(["<lista_init_deklaratora>", "ZAREZ", "<init_deklarator>"]):
      self.lista_init_deklaratora(inherited_type)
      self.assert_leaf("ZAREZ")
      self.init_deklarator(inherited_type)
    else:
      return self.parse_error(curr_line)

  """INIT DEKLARATOR"""
  def init_deklarator(self, inherited_type):
    curr_line = self.lines._iter
    pprint("# init_deklarator")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izravni_deklarator>"]):
      expr, num = self.izravni_deklarator(inherited_type)
      if expr.is_const:
        return self.parse_error(curr_line)
    elif self.check_expressions(["<izravni_deklarator>", "OP_PRIDRUZI", "<inicijalizator>"]):
      expr, num = self.izravni_deklarator(inherited_type)
      self.assert_leaf("OP_PRIDRUZI")
      expr2, num2 = self.inicijalizator()
      if not expr.is_array and not expr2.is_function:
        if not expr == expr2:
          return self.parse_error(curr_line)
      if not expr.is_array and expr2.is_function:
        if not expr == expr2.get_return_type():
          return self.parse_error(curr_line)
      elif expr.is_array:
        if not num >= num2:
          return self.parse_error(curr_line)
        if type(expr2) is list:
          _expr = Expr(expr)
          _expr.is_array = False
          [print(e) for e in expr2]
          for e in expr2:
            if not e == _expr:
              return self.parse_error(curr_line)
        else:
          if not expr2 == expr:
            return self.parse_error(curr_line)
    else:
      return self.parse_error(curr_line)

  """IZRAVNI DEKLARATOR"""
  def izravni_deklarator(self, inherited_type):
    curr_line = self.lines._iter
    pprint("# izravni_deklarator")
    pprint(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      idn = self.assert_leaf("IDN")
      if inherited_type == Expr("VOID"):
        return self.parse_error(curr_line)
      if self.table.contains(idn):
        return self.parse_error(curr_line)
      self.table.declare_var(idn, inherited_type)
      ## Returning false to know that it's not a declaration that returns a number as second arg
      return inherited_type, 1
    elif self.check_expressions(["IDN", "L_UGL_ZAGRADA", "BROJ", "D_UGL_ZAGRADA"]):
      _inherited_type = Expr(inherited_type).set_to_array()
      idn = self.assert_leaf("IDN")
      if _inherited_type == Expr("VOID"):
        return self.parse_error(curr_line)
      if self.table.contains(idn):
        return self.parse_error(curr_line)
      self.assert_leaf("L_UGL_ZAGRADA")
      num = self.assert_leaf("BROJ")
      if int(num) < 0 or int(num) > 1024:
        return self.parse_error(curr_line)
      self.table.declare_var(idn, _inherited_type)
      self.assert_leaf("D_UGL_ZAGRADA")
      return _inherited_type, int(num)
    elif self.check_expressions(["IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"]):
      idn = self.assert_leaf("IDN")
      self.assert_leaf("L_ZAGRADA")
      self.assert_leaf("KR_VOID")
      self.assert_leaf("D_ZAGRADA")
      if self.table.is_JUST_declared(idn) \
          and not self.table.is_declared(idn, [Expr("VOID")], [inherited_type]):
        return self.parse_error(curr_line)
      elif not self.table.is_JUST_declared(idn):
        self.table.declare_fun(idn, [Expr("VOID")], [inherited_type])
      else:
        pass # It means it's already declared and of same type
      ## Returning false to know that it's not a declaration that returns a number as second arg
      return Expr("VOID", is_function = True, fun_from = [Expr("VOID")], fun_to = [inherited_type]), 1
    elif self.check_expressions(["IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"]):
      idn = self.assert_leaf("IDN")
      self.assert_leaf("L_ZAGRADA")
      params, names = self.lista_parametara()
      self.assert_leaf("D_ZAGRADA")
      if self.table.is_JUST_declared(idn) \
          and not self.table.is_declared(idn, params, [inherited_type]):
        return self.parse_error(curr_line)
      elif not self.table.is_JUST_declared(idn):
        self.table.declare_fun(idn, params, [inherited_type])
      else:
        pass # It means it's already declared and of same type
      ## Returning false to know that it's not a declaration that returns a number as second arg
      return Expr("VOID", is_function = True, fun_from = params, fun_to = [inherited_type]), 1
    else:
      return self.parse_error(curr_line)

  """INICIJALIZATOR"""
  def inicijalizator(self):
    curr_line = self.lines._iter
    pprint("# inicijalizator")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      expr = self.izraz_pridruzivanja()
      if expr == Expr("CHAR", is_array = True):
        return Expr("CHAR", is_array = True), expr.array_length
      else:
        return expr, 1
    elif self.check_expressions(["L_VIT_ZAGRADA", "<lista_izraza_pridruzivanja>", "D_VIT_ZAGRADA"]):
      self.assert_leaf("L_VIT_ZAGRADA")
      expr, num = self.lista_izraza_pridruzivanja()
      self.assert_leaf("D_VIT_ZAGRADA")
      return expr, num
    else:
      return self.parse_error(curr_line)

  """LISTA IZRAZA PRIDRUZIVANJA"""
  def lista_izraza_pridruzivanja(self):
    curr_line = self.lines._iter
    pprint("# lista_izraza_pridruzivanja")
    pprint(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      expr = self.izraz_pridruzivanja()
      return [expr], 1
    elif self.check_expressions(["<lista_izraza_pridruzivanja>", "ZAREZ", "<izraz_pridruzivanja>"]):
      expr, num = self.lista_izraza_pridruzivanja()
      self.assert_leaf("ZAREZ")
      expr2 = self.izraz_pridruzivanja()
      return (expr + [expr2]), (num + 1)
    else:
      return self.parse_error(curr_line)

