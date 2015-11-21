__author__ = 'Mihael'
#!/usr/bin/env python3

import fileinput
import pickle
import PPJ.Lab2.analizator.TableFromGrammar2
import  PPJ.Lab2.analizator.TableFromGrammar3


definitions = pickle.load( open( 'analizator/temporary_definitions.bin', 'rb' ) )

V = definitions['nezavrsni']
T = definitions['terminali']
Syn = definitions['sinkronizacija']
P = definitions['produkcije']
SW = definitions['starts_with']
iduEpsilon = definitions['iduEpsilon']
maker = PPJ.Lab2.analizator.TableFromGrammar2.MakeProducitons(P, SW, T, V, iduEpsilon, '<%>')
#maker =  PPJ.Lab2.analizator.TableFromGrammar3.MakeProducitons(P, SW, T, V, '<%>')
LRTable = maker.give_table_from_DKAStates()
print(len(LRTable))
#for state in LRTable:
    #for key in LRTable[state]:
      #  print (key, state)
LRTable["sync"] = [";"]

lines = (line.rstrip() for line in fileinput.input())
listOfInputTupes = []

for line in lines:
    tuple = line.split (" ", 1)
    # print (tuple[0], "razmak",  tuple[1])
    listOfInputTupes.append(tuple)



class ParsingError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

stack = [0]

def advance(sym):
   # print ("sym", sym[0])
    global stack
    st = stack[-1]
    print (sym[0]," ",LRTable[st].keys())
    if sym[0] in LRTable[st].keys():
        print(sym[0])
        t, *ac = LRTable[st][sym[0]]
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
    if (len(h[0]) == 2):
        print (" "*i + str(h[0][0]) +" "+ str(h[0][1]))
    else:
         print (" "*i + str(h[0]))
    if len(h) < 2: # not sure if best way
        return
    for l in h[1]:
        pp(l, i + 1)


listOfInputTupes.append('$')

#print (listOfInputTupes)
for c in listOfInputTupes:
    try:
        advance(c)
    except ParsingError:
        # Error recovery
        print("Error while parsing...", c)
        synChar = c
        while not (synChar in LRTable["sync"]):
            try:
                synChar = next(listOfInputTupes)
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
