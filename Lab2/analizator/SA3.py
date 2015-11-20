__author__ = 'Mihael'
#!/usr/bin/env python3

import fileinput
import pickle
import PPJ.Lab2.analizator.TableFromGrammar



definitions = pickle.load( open( 'temporary_definitions.bin', 'rb' ) )

V = definitions['nezavrsni']
T = definitions['terminali']
Syn = definitions['sinkronizacija']
P = definitions['produkcije']
SW = definitions['starts_with']

maker = PPJ.Lab2.analizator.TableFromGrammar2.MakeProducitons(P, SW, T, V, '<%>')
LRTable = maker.give_table_from_DKAStates()
LRTable["sync"] = [";"]


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
                ssymbols = ['$'] #not sure if best way

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
    if len(h) < 2: # not sure if best way
        return
    for l in h[1]:
        pp(l, i + 1)

inp = iter("abaab$")
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
