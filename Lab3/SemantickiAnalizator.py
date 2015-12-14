from Table import Table
from Expr import Expr
from Lines import Lines
from helpers import extract_4

class SemantickiAnalizator:
  def __init__(self, lines):
    self.table = Table()
    self.lines = Lines(lines)
    return

#"""CHECK EXPRESSIONS""""
  def check_expressions(self, expressions):
    return self.lines.check_expressions(expressions)

#"""CHECK LEAF""""
  def check_leaf(self, fst_exp, snd_exp = ""):
    _, _fst_exp, _, _snd_exp = extract_4(self.lines.get_line())
    if not _fst_exp == fst_exp or (not _snd_exp == snd_exp and not snd_exp == ""):
      self.parse_error()
    else:
      self.lines.next()
      return snd_exp

#"""
  def check_both_for_int_and_return_int(self, fst_fun, expr, snd_fun):
    if not fst_fun().is_type("INT"):
      self.parse_error()
    self.check_leaf(expr)
    if not snd_fun().is_type("INT"):
      self.parse_error()
    return Expr("INT")


#"""IS SAME TYPE"""
  def is_same_type(self, fst_exp, snd_exp):
    return fst_exp.is_type("CHAR") and snd_exp.is_type("INT") \
        or (fst_exp.is_const() or snd_exp.is_const()) and fst_exp.is_type(snd_exp.get_type()) \
          and not fst_exp.is_function()

#"""CAN CAST"""
  def can_cast(self, fst_exp, snd_type):
    return self.is_same_type(fst_exp, snd_exp) \
        or fst_exp.is_type("INT") and snd_exp.is_type("CHAR")

  def parse_error(self):
    raise Exception("Parser error on line: " + str(self.lines.get_line()))

  def start(self):
    print("Starting and checking for <prijevodna_jedinica>")
    self.check_expressions(["<prijevodna_jedinica>"])
    print("Calling self.prijevodna_jedinica()")
    self.prijevodna_jedinica()

######################################
############### IZRAZI ###############
######################################
#"""PRIMARNI IZRAZ"""
  def primarni_izraz(self):
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      return check_leaf("IDN")
    elif self.check_expressions(["BROJ"]):
      raise Exception("Validation not implemented")
      self.check_leaf("BROJ")
      return Expr("BROJ", False)
    elif self.check_expressions(["ZNAK"]):
      raise Exception("Validation not implemented")
      self.check_leaf("ZNAK")
      return Expr("ZNAK", 0)
    elif self.check_expressions(["NIZ_ZNAKOVA"]):
      raise Exception("Validation not implemented")
      self.check_leaf("NIZ_ZNAKOVA")
      return Expr("NIZ_ZNAKOVA", 0)
    elif self.check_expressions(["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]):
      self.check_leaf("L_ZAGRADA")
      expr = izraz()
      self.check_leaf("D_ZAGRADA")
      return expr
    else:
      self.parse_error()

#"""POSTFIX IZRAZI"""
  def postfiks_izraz(self):
    print("postfiks_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<primarni_izraz>"]):
      return primarni_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]):
      expr = self.postfiks_izraz()
      if not expr.is_array():
        self.parse_error()
      self.check_leaf("L_UGL_ZAGRADA")
      if not self.izraz().is_type("INT"):
        self.parse_error()
      self.check_leaf("D_UGL_ZAGRADA")
      return Expr(expr.get_type(), lexpr = (not expr.is_const()))
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      if not expr.is_function() or not expr.is_function_from(["VOID"]):
        self.parse_error()
      return Expr(expr.get_return_type())
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]):
      expr = self.postfiks_izraz()
      self.check_leaf("L_ZAGRADA")
      expr2 = self.lista_argumenata()
      self.check_leaf("D_ZAGRADA")
      if not expr.is_function() or not expr.is_function_from(expr2.get_type()):
        self.parse_error()
      return expr.get_return_type()
    elif self.check_expressions(["<postfiks_izraz>", "OP_INC"]):
      exp = self.postfiks_izraz()
      self.check_leaf("OP_INC")
      if not exp.is_lexpr() or not exp.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["<postfiks_izraz>", "OP_DEC"]):
      exp = self.postfiks_izraz()
      self.check_leaf("OP_DEC")
      if not exp.is_lexpr() or not exp.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    else:
      self.parse_error()

#"""LISTA ARGUMENATA"""
  def lista_argumenata(self):
    print("lista_argumenata")
    print(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return [self.izraz_pridruzivanja()]
    elif self.check_expressions(["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]):
      expr = self.lista_argumenata()
      self.check_leaf("ZAREZ")
      return expr.append(self.izraz_pridruzivanja())
    else:
      self.parse_error()

#"""UNARNI IZRAZ"""
  def unarni_izraz(self):
    print("unarni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<postfiks_izraz>"]):
      return self.postfiks_izraz()
    elif self.check_expressions(["OP_DEC", "<unarni_izraz>"]):
      self.check_leaf("OP_DEC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr() or not expr.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["OP_INC", "<unarni_izraz>"]):
      self.check_leaf("OP_INC")
      expr = self.unarni_izraz()
      if not expr.is_lexpr() or not expr.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    elif self.check_expressions(["<unarni_operator>", "<cast_izraz>"]):
      expr = self.cast_izraz()
      if not expr.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    else:
      self.parse_error()

#"""UNARNI OPERATOR"""
  def unarni_operator(self):
    print("unarni_operator")
    print(self.lines.get_line())

    if self.check_expressions(["PLUS"]):
      self.check_leaf("PLUS")
      return
    elif self.check_expressions(["MINUS"]):
      self.check_leaf("MINUS")
      return
    elif self.check_expressions(["OP_TILDA"]):
      self.check_leaf("OP_TILDA")
      return
    elif sself.check_expressions(["OP_NEG"]):
      self.check_leaf("OP_NEG")
      return
    else:
      self.parse_error()

#"""CAST IZRAZ"""
  def cast_izraz(self):
    print("cast_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<unarni_izraz>"]):
      return self.unarni_izraz()
    elif self.check_expressions(["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]):
      self.check_leaf("L_ZAGRADA")
      expr = self.ime_tipa()
      self.check_leaf("D_ZAGRADA")
      expr2 = self.cast_izraz()
      if not self.can_cast(expr.get_type(), expr2.get_type()):
        self.parse_error()
      else:
        return Expr(expr.get_type(), False)

#"""IME TIPA"""
  def ime_tipa(self):
    print("ime_tipa")
    print(self.lines.get_line())

    if self.check_expressions(["<specifikator_tipa>"]):
      return self.specifikator_tipa()
    elif self.check_expressions(["KR_CONST", "<specifikator_tipa>"]):
      self.check_leaf("KR_CONST")
      expr = self.specifikator_tipa()
      if expr.is_type("VOID"):
        self.parse_error()
      else:
        return Expr(expr.get_type(), is_const = True)
    else:
      self.parse_error()

#"""SPECIFIKATOR TIPA"""
  def specifikator_tipa(self):
    print("specifikator_tipa")
    print(self.lines.get_line())

    if self.check_expressions(["KR_VOID"]):
      self.check_leaf("KR_VOID", "void")
      return Expr("VOID", False)
    elif self.check_expressions(["KR_CHAR"]):
      self.check_leaf("KR_CHAR", "char")
      return Expr("CHAR", False)
    elif self.check_expressions(["KR_INT"]):
      self.check_leaf("KR_INT", "int")
      return Expr("INT", False)
    else:
      self.parse_error()

#"""MULTIPLIKATIVNI IZRAZ"""
  def multiplikativni_izraz(self):
    print("multiplikativni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<cast_izraz>"]):
      return self.cast_izraz()
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_PUTA", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_PUTA", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_DIJELI", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_DIJELI", self.cast_izraz)
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_MOD", "<cast_izraz>"]):
      return self.check_both_for_int_and_return_int(self.multiplikativni_izraz, "OP_MOD", self.cast_izraz)
    else:
      self.parse_error()

#"""ADITIVNI IZRAZ"""
  def aditivni_izraz(self):
    print("aditivni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<multiplikativni_izraz>"]):
      return self.multiplikativni_izraz()
    elif self.check_expressions(["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.aditivni_izraz, "PLUS", self.multiplikativni_izraz)
    elif self.check_expressions(["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.aditivni_izraz, "MINUS", self.multiplikativni_izraz)
    else:
      self.parse_error()

#"""ODNOSNI IZRAZ"""
  def odnosni_izraz(self):
    print("odnosni_izraz")
    print(self.lines.get_line())

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
      self.parse_error()

#"""JEDNAKOSNI IZRAZ"""
  def jednakosni_izraz(self):
    print("jednakosni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<odnosni_izraz>"]):
      return self.odnosni_izraz()
    elif self.check_expressions(["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.jednakosni_izraz, "OP_EQ", self.odnosni_izraz)
    elif self.check_expressions(["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.jednakosni_izraz, "OP_NEQ", self.odnosni_izraz)
    else:
      self.parse_error()

#"""BIN I IZRAZ"""
  def bin_i_izraz(self):
    print("bin_i_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<jednakosni_izraz>"]):
      return self.jednakosni_izraz()
    elif self.check_expressions(["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_i_izraz, "OP_BIN_I", self.jednakosni_izraz)
    else:
      self.parse_error()

#"""BIN XILI IZRAZ"""
  def bin_xili_izraz(self):
    print("bin_xili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_i_izraz>"]):
      return self.bin_i_izraz()
    elif self.check_expressions(["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_xili_izraz, "OP_BIN_XILI", self.bin_i_izraz)
    else:
      self.parse_error()

#"""BIN ILI IZRAZ"""
  def bin_ili_izraz(self):
    print("bin_ili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_xili_izraz>"]):
      return self.bin_xili_izraz()
    elif self.check_expressions(["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]):
      return self.check_both_for_int_and_return_int(self.bin_ili_izraz, "OP_BIN_ILI", self.bin_xili_izraz)
    else:
      self.parse_error()

#"""LOG I IZRAZ"""
  def log_i_izraz(self):
    print("log_i_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_ili_izraz>"]):
      return self.bin_ili_izraz()
    elif self.check_expressions(["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]):
      return self.check_both_for_int_and_return_int(self.log_i_izraz, "OP_I", self.bin_xili_izraz)
    else:
      self.parse_error()

#"""LOG ILI IZRAZ"""
  def log_ili_izraz(self):
    print("log_ili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<log_i_izraz>"]):
      return self.log_i_izraz()
    elif self.check_expressions(["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]):
      return self.check_both_for_int_and_return_int(self.log_ili_izraz, "OP_ILI", self.log_i_izraz)
    else:
      self.parse_error()

#"""IZRAZ PRIDRUZIVANJA"""
  def izraz_pridruzivanja(self):
    print("izraz_pridruzivanja")
    print(self.lines.get_line())

    if self.check_expressions(["<log_ili_izraz>"]):
      return self.log_ili_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]):
      expr = self.postfiks_izraz()
      if not expr.is_lexpr():
        self.parse_error()
      self.check_leaf("OP_PRIDRUZI")
      expr2 = self.izraz_pridruzivanja()
      if not expr.is_type(expr2.get_type()):
        self.parse_error()
      return Expr(expr.get_type())
    else:
      self.parse_error()

#"""IZRAZ"""
  def izraz(self):
    print("izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return izraz_pridruzivanja()
    elif self.check_expressions(["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]):
      izraz()
      self.check_leaf("ZAREZ")
      return Expr(izraz_pridruzivanja().get_type())


##################################
## NAREDBENA STRUKTURA PROGRAMA ##
##################################

#"""SLOZENA NAREDBA"""
  def slozena_naredba(self):
    print("slozena_naredba")
    print(self.lines.get_line())

    if self.check_expressions(["L_VIT_ZAGRADA", "<lista_naredbi>", "D_VIT_ZAGRADA"]):
      self.check_leaf("L_VIT_ZAGRADA")
      self.lista_naredbi()
      self.check_leaf("D_VIT_ZAGRADA")
    elif self.check_expressions(["L_VIT_ZAGRADA", "<lista_deklaracija>", "<lista_naredbi>"
                               , "D_VIT_ZAGRADA"]):
      self.check_leaf("L_VIT_ZAGRADA")
      self.lista_deklaracija()
      self.lista_naredbi()
      self.check_leaf("D_VIT_ZAGRADA")
    else:
      self.parse_error()

#"""LISTA NAREDBI"""
  def lista_naredbi(self):
    print("lista_naredbi")
    print(self.lines.get_line())

    if self.check_expressions(["<naredba>"]):
      self.naredba()
    elif self.check_expressions(["<lista_naredbi>", "<naredba>"]):
      self.lista_naredbi()
      self.naredba()
    else:
      self.parse_error()

#"""NAREDBA"""
  def naredba(self):
    print("naredba")
    print(self.lines.get_line())

    if self.check_expressions(["<slozena_naredba>"]):
      self.slozena_naredba()
    elif self.check_expressions(["<izraz_naredba>"]):
      self.izraz_naredba()
    elif self.check_expressions(["<naredba_grananja>"]):
      self.naredba_grananja()
    elif self.check_expressions(["<naredba_petlje>"]):
      self.naredba_petlje()
    elif self.check_expressions(["<naredba_skoka>"]):
      self.naredba_skoka()
    else:
      self.parse_error()

#"""IZRAZ NAREDBA"""
  def izraz_naredba(self):
    print("izraz_naredba")
    print(self.lines.get_line())

    if self.check_expressions(["TOCKAZAREZ"]):
      return Expr("INT", False)
    elif self.check_expressions(["<izraz>", "TOCKAZAREZ"]):
      return Expr(izraz().get_type(), False)
    else:
      self.parse_error()

#"""NAREDBA GRANANJA"""
  def naredba_grananja(self):
    print("naredba_grananja")
    print(self.lines.get_line())

    if self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      if not izraz().is_type("INT"):
        self.parse_error()
      naredba()
    elif self.check_expressions(["KR_IF", "L_ZAGRADA", "<izraz>"
                                ,"D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]):
      if not izraz().is_type("INT"):
        self.parse_error()
      naredba()
      naredba()
    else:
      self.parse_error()

#"""NAREDBA PETLJE"""
  def naredba_petlje(self):
    print("naredba_petlje")
    print(self.lines.get_line())

    if self.check_expressions(["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]):
      if not izraz().is_type("INT"):
        self.parse_error()
      naredba()
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"D_ZAGRADA", "<naredba>"]):
      izraz_naredba()
      if not izraz_naredba().is_type("INT"):
        self.parse_error()
      naredba()
    elif self.check_expressions(["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>"
                                ,"<izraz>", "D_ZAGRADA", "<naredba>"]):
      izraz_naredba()
      if not izraz_naredba().is_type("INT"):
        self.parse_error()
      izraz()
      naredba()
    else:
      self.parse_error()

#"""NAREDBA SKOKA"""
  def naredba_skoka(self):
    print("naredba_skoka")
    print(self.lines.get_line())

    if self.check_expressions(["KR_CONTINUE", "TOCKAZAREZ"]) or \
       self.check_expressions(["KR_BREAK", "TOCKAZAREZ"]):
      return
    elif self.check_expressions(["KR_RETURN", "TOCKAZAREZ"]):
      return
    elif self.check_expressions(["KR_RETURN", "<izraz>", "TOCKAZAREZ"]):
      raise Exception("need pov impl")

#"""PRIJEVODNA JEDINICA"""
  def prijevodna_jedinica(self):
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    if self.check_expressions(["<vanjska_deklaracija>"]):
      print("<vanjska_deklaracija>")
      self.vanjska_deklaracija()
    elif self.check_expressions(["<prijevodna_jedinica>", "<vanjska_deklaracija>"]):
      print("<prijevodna_jedinica> <vanjska_deklaracija>")
      self.prijevodna_jedinica()
      self.vanjska_deklaracija()
    else:
      self.parse_error()

#"""VANJSKA DEKLARACIJA"""
  def vanjska_deklaracija(self):
    print("vanjska_deklaracija")
    print(self.lines.get_line())

    if self.check_expressions(["<definicija_funkcije>"]):
      self.definicija_funkcije()
    elif self.check_expressions(["<deklaracija>"]):
      self.deklaracija()
    else:
      self.parse_error()

##############################
## DEKLARACIJE I DEFINICIJE ##
##############################

#"""DEFINICIJA FUNKCIJE"""
  def definicija_funkcije(self):
    print("definicija_funkcije")
    print(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"
                             , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const():
        self.parse_error()
      idn = self.check_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        self.parse_error()
      ## 4
      if self.table.is_declared(idn, ["VOID"], expr.get_type()):
        self.parse_error()
      ## 5
      if not self.table.is_declared(idn, ["VOID"], expr.get_type()):
        self.table.declare(idn, ["VOID"], expr.get_type())
      if not self.table.is_defined(idn, ["VOID"], expr.get_type()):
        self.table.define(idn, ["VOID"], expr.get_type())
      ## X
      self.check_leaf("L_ZAGRADA")
      self.check_leaf("KR_VOID")
      self.check_leaf("D_ZAGRADA")
      ## 6
      self.slozena_naredba()
    elif self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"
                               , "<slozena_naredba>"]):
      ## 1
      expr = self.ime_tipa()
      ## 2
      if expr.is_const():
        self.parse_error()
      idn = self.check_leaf("IDN")
      ## 3
      if self.table.contains(idn) and self.table.is_defined(idn):
        self.parse_error()
      ## X
      self.check_leaf("L_ZAGRADA")
      ## 4
      expr2 = lista_parametara()
      ## 5
      if self.table.is_declared(idn) and \
          not (self.table.is_function_from(idn, expr2.get_type()) \
            and self.table.is_function_to(idn, expr.get_type())):
        self.parse_error()
      ## 6
      if not self.table.is_declared(idn, expr2.get_type(), expr.get_type()):
        self.table.declare(idn, expr2.get_type(), expr.get_type())
      if not self.table.is_defined(idn, expr2.get_type(), expr.get_type()):
        self.table.define(idn, expr2.get_type(), expr.get_type())
      ## X
      self.check_leaf("D_ZAGRADA")
      ## 7 !!! Careful about function parameters. Not yet implemented (i think)
      self.slozena_naredba()
      raise Exception("I think not yet implemented")
    else:
      self.parse_error()

#"""LISTA PARAMETARA"""
  def lista_parametara(self):
    print("lista_parametara")
    print(self.lines.get_line())

    if self.check_expressions(["<deklaracija_parametra>"]):
      return deklaracija_parametra()
    elif self.check_expressions(["<lista_parametara>", "ZAREZ", "<deklaracija_parametra>"]):
      tipovi, imena = lista_parametara()
      tip, ime = deklaracija_parametra()
      return tipovi.append(tip), imena.append(ime)
    else:
      self.parse_error()

#"""DEKLARACIJA PARAMETRA"""
  def deklaracija_parametra(self):
    print("deklaracija_parametra")
    print(self.lines.get_line())

    if self.check_expressions(["<ime_tipa>", "IDN"]):
      tip = ime_tipa().get_type()
      if tip == "VOID":
        self.parse_error()
      raise Exception("TODO")
    elif self.check_expressions(["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"]):
      tip = ime_tipa().get_type()
      if tip == "VOID":
        self.parse_error()
      raise Exception("TODO")

#"""LISTA DEKLARACIJA"""
  def lista_deklaracija(self):
    print("lista_deklaracija")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<deklaracija>"]) or \
      self.check_expressions(["<lista_deklaracija>", "<deklaracija>"])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def deklaracija(self):
    print("deklaracija")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<ime_tipa>", "<lista_init_deklaratora>", "TOCKAZAREZ"])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_init_deklaratora(self):
    print("lista_init_deklaratora")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<init_deklarator>"]) or \
      self.check_expressions(["<lista_init_deklaratora>", "ZAREZ", "<init_deklarator>"])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def init_deklarator(self):
    print("init_deklarator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<izravni_deklarator>"]) or \
      self.check_expressions(["<izravni_deklarator>", "OP_PRIDRUZI", "<inicijalizator>"])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def izravni_deklarator(self):
    print("izravni_deklarator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["IDN"]) or \
      self.check_expressions(["IDN", "L_UGL_ZAGRADA", "BROJ", "D_UGL_ZAGRADA"]) or \
      self.check_expressions(["IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"]) or \
      self.check_expressions(["IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def inicijalizator(self):
    print("inicijalizator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<izraz_pridruzivanja>"]) or \
      self.check_expressions(["L_VIT_ZAGRADA", "<lista_izraza_pridruzivanja>", "D_VIT_ZAGRADA"])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_izraza_pridruzivanja(self):
    print("lista_izraza_pridruzivanja")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<izraz_pridruzivanja>"]) or \
      self.check_expressions(["<lista_izraza_pridruzivanja>", "ZAREZ", "<izraz_pridruzivanja>"])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid