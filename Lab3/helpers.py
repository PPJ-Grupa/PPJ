import re

"""IS SAME TYPE"""
def is_same_type(self, fst_exp, snd_exp):
  return fst_exp.is_type("CHAR") and snd_exp.is_type("INT") \
      or (fst_exp.is_const or snd_exp.is_const) and fst_exp.is_type(snd_exp.get_type()) \
        and not fst_exp.is_function

def calculate_padding(word):
  count = 0
  for c in word:
    if c == ' ':
      count += 1
    else:
      return count
  print('Error in calculate_padding')
  return -1

def chop(sentence):
  word, _, rest = sentence.partition(' ')
  return word, rest

def extract_2(sentence):
  return chop(sentence)

def extract_3(sentence):
  fst, rest = chop(sentence)
  snd, trd = chop(rest)
  return fst, snd, trd

def extract_4(sentence):
  fst, rest = chop(sentence)
  snd, rest = chop(rest)
  trd, fth = chop(rest)
  return fst, snd, trd, fth

def is_valid_char_array(c_arr):
  for res in re.findall(r"\\.", c_arr):
    if not res == r"\t" and not res == r"\n" and \
        not res == r"\0" and not res == r"\'" and \
        not res == r"\"" and not res == r"\\":
        return False
  return True