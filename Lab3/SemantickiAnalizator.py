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

############
## IZRAZI ##
############

  def primarni_izraz(self):
    """ Barely implemented """
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['IDN']) or \
      self.check_expressions(['BROJ']) or \
      self.check_expressions(['ZNAK']) or \
      self.check_expressions(['NIZ_ZNAKOVA']) or \
      self.check_expressions(['L_ZAGRADA', '<izraz>', 'D_ZAGRADA'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def postfiks_izraz(self):
    print("postfiks_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<primarni_izraz>']) or \
      self.check_expressions(['<postfiks_izraz>', 'L_UGL_ZAGRADA', '<izraz>', 'D_UGL_ZAGRADA']) or \
      self.check_expressions(['<postfiks_izraz>', 'L_ZAGRADA', 'D_ZAGRADA']) or \
      self.check_expressions(['<postfiks_izraz>', 'L_ZAGRADA', '<lista_argumenata>', 'D_ZAGRADA']) or \
      self.check_expressions(['<postfiks_izraz>', 'OP_INC']) or \
      self.check_expressions(['<postfiks_izraz>', 'OP_DEC'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_argumenata(self):
    print("lista_argumenata")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<izraz_pridruzivanja>']) or \
      self.check_expressions(['<lista_argumenata>', 'ZAREZ', '<izraz_pridruzivanja>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def unarni_izraz(self):
    print("unarni_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<postfiks_izraz>']) or \
      self.check_expressions(['OP_INC', '<unarni_izraz>']) or \
      self.check_expressions(['OP_DEC', '<unarni_izraz>']) or \
      self.check_expressions(['<unarni_operator>', '<cast_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def unarni_operator(self):
    print("unarni_operator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['PLUS']) or \
      self.check_expressions(['MINUS']) or \
      self.check_expressions(['OP_TILDA']) or \
      self.check_expressions(['OP_NEG'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def cast_izraz(self):
    print("cast_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<unarni_izraz>']) or \
      self.check_expressions(['L_ZAGRADA', '<ime_tipa>', 'D_ZAGRADA', '<cast_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def ime_tipa(self):
    print("ime_tipa")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<specifikator_tipa>']) or \
      self.check_expressions(['KR_CONST', '<specifikator_tipa>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def specifikator_tipa(self):
    print("specifikator_tipa")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['KR_VOID']) or \
      self.check_expressions(['KR_CHAR']) or \
      self.check_expressions(['KR_INT'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def multiplikativni_izraz(self):
    print("multiplikativni_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<cast_izraz>']) or \
      self.check_expressions(['<multiplikativni_izraz>', 'OP_PUTA', '<cast_izraz>']) or \
      self.check_expressions(['<multiplikativni_izraz>', 'OP_DIJELI', '<cast_izraz>']) or \
      self.check_expressions(['<multiplikativni_izraz>', 'OP_MOD', '<cast_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def aditivni_izraz(self):
    print("aditivni_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<multiplikativni_izraz>']) or \
      self.check_expressions(['<aditivni_izraz>', 'PLUS', '<multiplikativni_izraz>']) or \
      self.check_expressions(['<aditivni_izraz>', 'MINUS', '<multiplikativni_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def jednakosni_izraz(self):
    print("jednakosni_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<odnosni_izraz>']) or \
      self.check_expressions(['<jednakosni_izraz>', 'OP_EQ', '<odnosni_izraz>']) or \
      self.check_expressions(['<jednakosni_izraz>', 'OP_NEQ', '<odnosni_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def bin_i_izraz(self):
    print("bin_i_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<jednakosni_izraz>']) or \
      self.check_expressions(['<bin_i_izraz>', 'OP_BIN_I', '<jednakosni_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def bin_xili_izraz(self):
    print("bin_xili_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<bin_i_izraz>']) or \
      self.check_expressions(['<bin_xili_izraz>', 'OP_BIN_XILI', '<bin_i_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def bin_ili_izraz(self):
    print("bin_ili_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<bin_xili_izraz>']) or \
      self.check_expressions(['<bin_ili_izraz>', 'OP_BIN_ILI', '<bin_xili_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def log_i_izraz(self):
    print("log_i_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<bin_ili_izraz>']) or \
      self.check_expressions(['<log_i_izraz>', 'OP_I', '<bin_ili_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def log_ili_izraz(self):
    print("log_ili_izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<log_i_izraz>']) or \
      self.check_expressions(['<log_ili_izraz>', 'OP_ILI', '<log_i_izraz>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def izraz_pridruzivanja(self):
    print("izraz_pridruzivanja")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<log_ili_izraz>']) or \
      self.check_expressions(['<postfiks_izraz>', 'OP_PRIDRUZI', '<izraz_pridruzivanja>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def izraz(self):
    print("izraz")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<izraz_pridruzivanja>']) or \
      self.check_expressions(['<izraz>', 'ZAREZ', '<izraz_pridruzivanja>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

##################################
## NAREDBENA STRUKTURA PROGRAMA ##
##################################

  def slozena_naredba(self):
    print("slozena_naredba")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['L_VIT_ZAGRADA', '<lista_naredbi>', 'D_VIT_ZAGRADA']) or \
      self.check_expressions(['L_VIT_ZAGRADA', '<lista_deklaracija>', '<lista_naredbi>', 'D_VIT_ZAGRADA'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_naredbi(self):
    print("lista_naredbi")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<naredba>']) or \
      self.check_expressions(['<lista_naredbi>', '<naredba>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def izraz_naredba(self):
    print("izraz_naredba")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['TOCKAZAREZ']) or \
      self.check_expressions(['<izraz>', 'TOCKAZAREZ'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def naredba_grananja(self):
    print("naredba_grananja")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']) or \
      self.check_expressions(['KR_IF', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>', 'KR_ELSE', '<naredba>'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def naredba_petlje(self):
    print("naredba_petlje")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['KR_WHILE', 'L_ZAGRADA', '<izraz>', 'D_ZAGRADA', '<naredba>']) or \
      self.check_expressions(['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', 'D_ZAGRADA', '<naredba>']) or \
      self.check_expressions(['KR_FOR', 'L_ZAGRADA', '<izraz_naredba>', '<izraz_naredba>', '<izraz>', 'D_ZAGRADA', '<naredba>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def naredba_skoka(self):
    print("naredba_skoka")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['KR_CONTINUE', 'TOCKAZAREZ']) or \
      self.check_expressions(['KR_BREAK', 'TOCKAZAREZ']) or \
      self.check_expressions(['KR_RETURN', 'TOCKAZAREZ']) or \
      self.check_expressions(['KR_RETURN', '<izraz>', 'TOCKAZAREZ'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def prijevodna_jedinica(self):
    print("prijevodna_jedinica")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<vanjska_deklaracija>']) or \
      self.check_expressions(['<prijevodna_jedinica>', '<vanjska_deklaracija>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def vanjska_deklaracija(self):
    print("vanjska_deklaracija")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<definicija_funkcije>']) or \
      self.check_expressions(['<deklaracija>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

##############################
## DEKLARACIJE I DEFINICIJE ##
##############################

  def definicija_funkcije(self):
    print("definicija_funkcije")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<ime_tipa>', 'IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA', '<slozena_naredba>']) or \
      self.check_expressions(['<ime_tipa>', 'IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA', '<slozena_naredba>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_parametara(self):
    print("lista_parametara")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<deklaracija_parametara>']) or \
      self.check_expressions(['<lista_parametara>', 'ZAREZ', '<deklaracija_parametara>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def deklaracija_parametara(self):
    print("deklaracija_parametara")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<ime_tipa>', 'IDN']) or \
      self.check_expressions(['<ime_tipa>', 'IDN', 'L_UGL_ZAGRADA', 'D_UGL_ZAGRADA'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_deklaracija(self):
    print("lista_deklaracija")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<deklaracija>']) or \
      self.check_expressions(['<lista_deklaracija>', '<deklaracija>'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def deklaracija(self):
    print("deklaracija")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<ime_tipa>', '<lista_init_deklaratora>', 'TOCKAZAREZ'])

    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_init_deklaratora(self):
    print("lista_init_deklaratora")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<init_deklarator>']) or \
      self.check_expressions(['<lista_init_deklaratora>', 'ZAREZ', '<init_deklarator>'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def init_deklarator(self):
    print("init_deklarator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<izravni_deklarator>']) or \
      self.check_expressions(['<izravni_deklarator>', 'OP_PRIDRUZI', '<inicijalizator>'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def izravni_deklarator(self):
    print("izravni_deklarator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['IDN']) or \
      self.check_expressions(['IDN', 'L_UGL_ZAGRADA', 'BROJ', 'D_UGL_ZAGRADA']) or \
      self.check_expressions(['IDN', 'L_ZAGRADA', 'KR_VOID', 'D_ZAGRADA']) or \
      self.check_expressions(['IDN', 'L_ZAGRADA', '<lista_parametara>', 'D_ZAGRADA'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def inicijalizator(self):
    print("inicijalizator")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<izraz_pridruzivanja>']) or \
      self.check_expressions(['L_VIT_ZAGRADA', '<lista_izraza_pridruzivanja>', 'D_VIT_ZAGRADA'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid

  def lista_izraza_pridruzivanja(self):
    print("lista_izraza_pridruzivanja")
    print(self.lines.get_line())

    valid = \
      self.check_expressions(['<izraz_pridruzivanja>']) or \
      self.check_expressions(['<lista_izraza_pridruzivanja>', 'ZAREZ', '<izraz_pridruzivanja>'])
      
    print(str(valid))
    if not valid:
      raise Exception("Parser error at:\n" + self.lines.get_line())
    return valid