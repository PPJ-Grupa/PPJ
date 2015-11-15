__author__ = 'Mihael'
#!/usr/bin/env python3

import fileinput
import json
# R -> reduciraj, S -> shift dalje, G -> tablica novo stanje, A -> prihvati
##
# ("R", koliko simbol konzumiram, koji simbol stavljam, zaKojestanje)
# ("S", sljedece stanje)
# ("A")
# ("G", stanje)
## Example language:
## S -> AA
## A -> aA | b
## LR(0) example parsing table
## error handling je zesce nastiman na ovaj primjer
LRTable = {0: {'b': ('S', 4), 'a': ('S', 5), '<A>': ('G', 1), '$': ('R', 0, '<A>'), '<B>': ('G', 6)}, 1: {'$': 'A'}, 2: {'$': ('R', 2, '<A>')}, 3: {'b': ('R', 2, '<B>'), '$': ('R', 2, '<B>'), 'a': ('R', 2, '<B>')}, 4: {'b': ('R', 1, '<B>'), '$': ('R', 1, '<B>'), 'a': ('R', 1, '<B>')}, 5: {'b': ('S', 4), 'a': ('S', 5), '<B>': ('G', 3)}, 6: {'b': ('S', 4), 'a': ('S', 5), '<A>': ('G', 2), '$': ('R', 0, '<A>'), '<B>': ('G', 6)}

, "sync":[";"]}


class ParsingError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

stack = [0]

def advance(sym):
    #print (sym)
    global stack
    st = stack[-1]
    if sym in LRTable[st].keys():
        t, *ac = LRTable[st][sym]
        if t == "R": #reduce
            n, lhs = ac # lhs is left hand side of production
            if n != 0:
                 ssymbols = stack[-2*n:-1:2]
                 stack = stack[:-2*n]
            else :
                ssymbols = []

            stcur = stack[-1]

            stack.append((lhs, ssymbols))

            # goto executing
            if not lhs in LRTable[stcur]:
                raise ParsingError("No transition")
            stack.append(LRTable[stcur][lhs][1])
            #print (stcur, sym)
            advance(sym)
            # jedna iteracija reduca
        elif t == "S": # shift
            stack.append((sym, []))
            stack.append(ac[0])
        elif t == "A":
            return
        else:
            print ("ERROR Uknown action")
    else:
        raise ParsingError("No transition")

def pp(h, i = 0):
    print (" "*i + str(h[0]))
    for l in h[1]:
        pp(l, i + 1)

inp = iter("aaab$")
for c in inp:
    try:
        advance(c)
    except ParsingError:
        # Error recovery
        print("Error while parsing...", c)
        synChar = c
        while not (synChar in LRTable["sync"]):
            try:
                synChar = next(inp)
            except StopIteration:
                raise ParsingError("Parsing finished with errors")
        try:
            while synChar not in LRTable[stack[-1]].keys():
                stack.pop()
                stack.pop()
        except IndexError:
            raise ParsingError("Parsing finished with errors")
        advance(synChar)

pp(stack[1])
