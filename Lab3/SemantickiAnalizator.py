from Table import Table
from Expr import Expr
from Lines import Lines

class SemantickiAnalizator:
  def __init__(self, lines):
    self.table = Table()
    self.lines = Lines(lines)
    return

  def check_expressions(self, expressions):
    return self.lines.check_expressions(expressions)

  def start(self):
    self.check_expressions(["<prijevodna_jedinica>"])
    self.prijevodna_jedinica()

######################################
############### IZRAZI ###############
######################################
"""PRIMARNI IZRAZ"""
  def primarni_izraz(self):
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    if self.check_expressions(["IDN"]):
      _, _, _, var_name = extract_4(self.lines.get_line())
      if not self.table.contains(var_name):
        raise Exception("var not in table")
      return self.table.get_var(var_name)
    elif self.check_expressions(["BROJ"]):
      return Expr("BROJ", False)
    elif self.check_expressions(["ZNAK"]):
      return Expr("ZNAK", 0)
    elif self.check_expressions(["NIZ_ZNAKOVA"]):
      return Expr("NIZ_ZNAKOVA", 0)
    elif self.check_expressions(["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]):
      return izraz()
    else:
      self.parse_error()

"""POSTFIX IZRAZI"""
  def postfiks_izraz(self):
    print("postfiks_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<primarni_izraz>"]):
      return primarni_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]):
      raise Exception("What is X in docs?")
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]):
      raise Exception("What is pov in docs?")
    elif self.check_expressions(["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]):
      raise Exception("What is pov in docs?")
    elif self.check_expressions(["<postfiks_izraz>", "OP_INC"]) or \
         self.check_expressions(["<postfiks_izraz>", "OP_DEC"]):
      exp = self.postfiks_izraz()
      if not exp.is_lexpr() or not exp.is_type("INT"):
        self.parse_error()
      else:
        return Expr("INT", False)
    else:
      self.parse_error()

"""LISTA ARGUMENATA"""
  def lista_argumenata(self):
    print("lista_argumenata")
    print(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return [self.izraz_pridruzivanja()]
    elif self.check_expressions(["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]):
      return self.lista_argumenata().append(self.izraz_pridruzivanja())
    else:
      self.parse_error()

"""UNARNI IZRAZ"""
  def unarni_izraz(self):
    print("unarni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<postfiks_izraz>"]):
      return self.postfiks_izraz()
    elif self.check_expressions(["OP_INC", "<unarni_izraz>"]) or \
         self.check_expressions(["OP_DEC", "<unarni_izraz>"]):
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

"""UNARNI OPERATOR"""
  def unarni_operator(self):
    print("unarni_operator")
    print(self.lines.get_line())

    if self.check_expressions(["PLUS"]) or 
      self.check_expressions(["MINUS"]) or \
      self.check_expressions(["OP_TILDA"]) or \
      self.check_expressions(["OP_NEG"]):
      return
    else:
      self.parse_error()

"""CAST IZRAZ"""
  def cast_izraz(self):
    print("cast_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<unarni_izraz>"]):
      return self.unarni_izraz()
    elif self.check_expressions(["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]):
      expr = self.ime_tipa()
      expr2 = self.cast_izraz()
      if not can_cast(expr.get_type(), expr2.get_type()):
        self.parse_error()
      else:
        return Expr(expr.get_type(), False)

"""IME TIPA"""
  def ime_tipa(self):
    print("ime_tipa")
    print(self.lines.get_line())

    if self.check_expressions(["<specifikator_tipa>"]):
      return self.specifikator_tipa()
    elif self.check_expressions(["KR_CONST", "<specifikator_tipa>"]):
      expr = self.specifikator_tipa()
      if expr.is_type("VOID"):
        self.parse_error()
      else:
        return Expr(const(expr.get_type()), False)
    else:
      self.parse_error()

"""SPECIFIKATOR TIPA"""
  def specifikator_tipa(self):
    print("specifikator_tipa")
    print(self.lines.get_line())

    if self.check_expressions(["KR_VOID"]):
      return Expr("VOID", False)
    elif self.check_expressions(["KR_CHAR"]):
      return Expr("CHAR", False)
    elif self.check_expressions(["KR_INT"]):
      return Expr("INT", False)
    else:
      self.parse_error()

"""MULTIPLIKATIVNI IZRAZ"""
  def multiplikativni_izraz(self):
    print("multiplikativni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<cast_izraz>"]):
      return self.cast_izraz()
    elif self.check_expressions(["<multiplikativni_izraz>", "OP_PUTA", "<cast_izraz>"]) or \
         self.check_expressions(["<multiplikativni_izraz>", "OP_DIJELI", "<cast_izraz>"]) or \
         self.check_expressions(["<multiplikativni_izraz>", "OP_MOD", "<cast_izraz>"]):
      return check_both_for_int_and_return_int(self.multiplikativni_izraz, self.cast_izraz)
    else:
      self.parse_error()

"""ADITIVNI IZRAZ"""
  def aditivni_izraz(self):
    print("aditivni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<multiplikativni_izraz>"]):
      return self.multiplikativni_izraz()
    elif self.check_expressions(["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]) or \
         self.check_expressions(["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]):
      return check_both_for_int_and_return_int(self.aditivni_izraz, self.multiplikativni_izraz)
    else:
      self.parse_error()

"""ODNOSNI IZRAZ"""
  def odnosni_izraz(self):
    print("odnosni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<aditivni_izraz>"]):
      return aditivni_izraz()
    elif self.check_expressions(["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"]) or \
         self.check_expressions(["<odnosni_izraz>", "OP_GZ", "<aditivni_izraz>"]) or \
         self.check_expressions(["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"]) or \
         self.check_expressions(["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]):
      return check_both_for_int_and_return_int(self.odnosni_izraz, self.aditivni_izraz)
    else:
      self.parse_error()

"""JEDNAKOSNI IZRAZ"""
  def jednakosni_izraz(self):
    print("jednakosni_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<odnosni_izraz>"]):
      return self.odnosni_izraz()
    elif self.check_expressions(["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]) or \
      self.check_expressions(["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]):
      return check_both_for_int_and_return_int(self.jednakosni_izraz, self.odnosni_izraz)

"""BIN I IZRAZ"""
  def bin_i_izraz(self):
    print("bin_i_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<jednakosni_izraz>"]):
      return jednakosni_izraz()
    elif self.check_expressions(["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]):
      return check_both_for_int_and_return_int(self.bin_i_izraz, self.jednakosni_izraz)
    else:
      self.parse_error()

"""BIN XILI IZRAZ"""
  def bin_xili_izraz(self):
    print("bin_xili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_i_izraz>"]):
      return self.bin_i_izraz()
    elif self.check_expressions(["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]):
      return check_both_for_int_and_return_int(self.bin_xili_izraz, self.bin_i_izraz)
    else:
      self.parse_error()

"""BIN ILI IZRAZ"""
  def bin_ili_izraz(self):
    print("bin_ili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_xili_izraz>"]):
      return self.bin_xili_izraz()
    elif self.check_expressions(["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]):
      return check_both_for_int_and_return_int(self.bin_ili_izraz, self.bin_xili_izraz)
    else:
      self.parse_error()

"""LOG I IZRAZ"""
  def log_i_izraz(self):
    print("log_i_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<bin_ili_izraz>"]):
      return self.bin_ili_izraz()
    elif self.check_expressions(["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]):
      return check_both_for_int_and_return_int(self.log_i_izraz, self.bin_xili_izraz)
    else:
      self.parse_error()

"""LOG ILI IZRAZ"""
  def log_ili_izraz(self):
    print("log_ili_izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<log_i_izraz>"]):
      return self.log_i_izraz()
    elif self.check_expressions(["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]):
      return check_both_for_int_and_return_int(self.log_ili_izraz, self.log_i_izraz)
    else:
      self.parse_error()

"""IZRAZ PRIDRUZIVANJA"""
  def izraz_pridruzivanja(self):
    print("izraz_pridruzivanja")
    print(self.lines.get_line())

    if self.check_expressions(["<log_ili_izraz>"]):
      return log_ili_izraz()
    elif self.check_expressions(["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]):
      expr = postfiks_izraz()
      if not expr.is_lexpr():
        self.parse_error()
      expr2 = izraz_pridruzivanja()
      if not expr.is_type(expr2.get_type()):
        self.parse_error()
      return Expr(expr.get_type(), False)
    else:
      self.parse_error()

"""IZRAZ"""
  def izraz(self):
    print("izraz")
    print(self.lines.get_line())

    if self.check_expressions(["<izraz_pridruzivanja>"]):
      return izraz_pridruzivanja()
    elif self.check_expressions(["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]):
      izraz()
      return Expr(izraz_pridruzivanja().get_type(), False)


##################################
## NAREDBENA STRUKTURA PROGRAMA ##
##################################

"""SLOZENA NAREDBA"""
  def slozena_naredba(self):
    print("slozena_naredba")
    print(self.lines.get_line())

    if self.check_expressions(["L_VIT_ZAGRADA", "<lista_naredbi>", "D_VIT_ZAGRADA"]):
      self.lista_naredbi()
    elif self.check_expressions(["L_VIT_ZAGRADA", "<lista_deklaracija>", "<lista_naredbi>", "D_VIT_ZAGRADA"]):
      self.lista_deklaracija()
      self.lista_naredbi()
    else:
      self.parse_error()

"""LISTA NAREDBI"""
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

"""IZRAZ NAREDBA"""
  def izraz_naredba(self):
    print("izraz_naredba")
    print(self.lines.get_line())

    if self.check_expressions(["TOCKAZAREZ"]):
      return Expr("INT", False)
    elif self.check_expressions(["<izraz>", "TOCKAZAREZ"]):
      return Expr(izraz().get_type(), False)
    else:
      self.parse_error()

"""NAREDBA GRANANJA"""
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

"""NAREDBA PETLJE"""
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

"""NAREDBA SKOKA"""
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

"""PRIJEVODNA JEDINICA"""
  def prijevodna_jedinica(self):
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    if self.check_expressions(["<vanjska_deklaracija>"]):
      vanjska_deklaracija()
    elif self.check_expressions(["<prijevodna_jedinica>", "<vanjska_deklaracija>"]):
      prijevodna_jedinica()
      vanjska_deklaracija()
    else:
      self.parse_error()

"""VANJSKA DEKLARACIJA"""
  def vanjska_deklaracija(self):
    print("vanjska_deklaracija")
    print(self.lines.get_line())

    if self.check_expressions(["<definicija_funkcije>"]):
      self.definicija_funkcije()
    elif self.check_expressions(["<deklaracija>"]):
      deklaracija()
    else:
      self.parse_error()
      
##############################
## DEKLARACIJE I DEFINICIJE ##
##############################

  def definicija_funkcije(self):
    print("definicija_funkcije")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA", "<slozena_naredba>"]) or \
      self.check_expressions(["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA", "<slozena_naredba>"])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_parametara(self):
    print("lista_parametara")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<deklaracija_parametara>"]) or \
      self.check_expressions(["<lista_parametara>", "ZAREZ", "<deklaracija_parametara>"])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def deklaracija_parametara(self):
    print("deklaracija_parametara")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(["<ime_tipa>", "IDN"]) or \
      self.check_expressions(["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

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