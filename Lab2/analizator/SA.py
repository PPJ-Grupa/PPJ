#!/usr/bin/env python3

import fileinput
import json
from collections import defaultdict
from functools import lru_cache, reduce
import operator

##
# ("R", koliko simbol konzumiram, koji simbol stavljam)
# ("S", sljedece stanje)
# ("A")
# ("G", stanje)
## Example language:
## S -> AA
## A -> aA | b
## LR(0) example parsing table
LRTable = {
    0: {"a" : ("S", 3), "b" : ("S", 4), "A" : ("G", 2), "S" : ("G", 1)},
    1: {"$" : ("A")},
    2: {"a" : ("S", 3), "b": ("S", 4), "A" : ("G", 5)},
    3: {"a" : ("S", 3), "b": ("S", 4), "A" : ("G", 6)},
    4: {x : ("R" , 1, "A") for x in ["a", "b", "$"]},
    5: {x : ("R" , 2, "S") for x in ["a", "b", "$"]},
    6: {x : ("R" , 2, "A") for x in ["a", "b", "$"]}
}
stack = [0]

def advance(sym):
    global stack
    st = stack[-1]
    if sym in LRTable[st].keys():
        t, *ac = LRTable[st][sym]
        if t == "R": #reduce
            n, ss = ac
            ssymbols = stack[-2*n:-1:2]
            stack = stack[:-2*n]
            st = stack[-1]
            stack.append((ss, ssymbols))
            stack.append(LRTable[st][ss][1])
            advance(sym)
            # jedna iteracija reduca
        elif t == "S": # shift
            stack.append((sym, []))
            stack.append(ac[0])
        elif t == "G": # goto
            stack.pop()
            stack.append(ac[0])
            advance(sym)
        elif t == "A":
            print ("Accepted")
        else:
            print ("ERROR Uknown action")
    else:
        print ("ERROR.. not found")

def pp(h, i = 0):
    print (" "*i + str(h[0]))
    for l in h[1]:
        pp(l, i + 1)

# print (stack)
for c in "aabb$":
    advance(c)
    # print ("letter = ", c, stack)

pp(stack[1])
