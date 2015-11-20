#!/usr/bin/env python3

import fileinput
import json

##
# ("R", koliko simbol konzumiram, koji simbol stavljam)
# ("S", sljedece stanje)
# ("A")
# ("G", stanje)
## Example language:
## S -> AA
## A -> aA | b
## LR(0) example parsing table
## error handling je zesce nastiman na ovaj primjer
LRTable = {
    0: {"a" : ("S", 3), "b" : ("S", 4), "A" : ("G", 2), "S" : ("G", 1), ";" : ("S", 0)},
    1: {"$" : ("A")},
    2: {"a" : ("S", 3), "b": ("S", 4), "A" : ("G", 5)},
    3: {"a" : ("S", 3), "b": ("S", 4), "A" : ("G", 6)},
    4: {x : ("R" , 1, "A") for x in ["a", "b", "$"]},
    5: {x : ("R" , 2, "S") for x in ["a", "b", "$"]},
    6: {x : ("R" , 2, "A") for x in ["a", "b", "$"]},
    "sync" : [";"]
}

class ParsingError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

stack = [0]

def advance(sym):
    global stack
    st = stack[-1]
    if sym in LRTable[st].keys():
        t, *ac = LRTable[st][sym]
        if t == "R": #reduce
            n, lhs = ac # lhs is left hand side of production
            ssymbols = stack[-2*n:-1:2]
            stack = stack[:-2*n]
            st = stack[-1]
            stack.append((lhs, ssymbols))

            # goto executing
            if not lhs in LRTable[st]:
                raise ParsingError("No transition")
            stack.append(LRTable[st][lhs][1])
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

inp = iter("aabb$")
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
