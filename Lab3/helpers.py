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