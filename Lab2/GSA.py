#!/usr/bin/env python3

import fileinput
import json
from collections import defaultdict
from functools import lru_cache, reduce
import operator

lines = (line.rstrip() for line in fileinput.input())

V = set(next(lines).split()[1:])
T = set(next(lines).split()[1:])
Syn = set(next(lines).split()[1:])
P = defaultdict(list)

vv = None
for line in lines:
    if line[0] == " ":
        P[vv].append(line.split())
    else:
        vv = line

@lru_cache(maxsize=None)
def startsWith(symbol):
        return set([symbol]) if symbol[0] != '<' else reduce(operator.__or__, (startsWith(a[0]) for a in P[symbol]))

SW = {key : list(startsWith(key)) for key in V}
print(json.dumps(P, sort_keys=True, indent=4, separators=(',', ': ')))
print(json.dumps(SW, sort_keys=True, indent=4, separators=(',', ': ')))
