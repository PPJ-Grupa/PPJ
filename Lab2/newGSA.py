#!/usr/bin/env python3

import fileinput
import json
from collections import defaultdict
from functools import lru_cache, reduce
import operator

# imamo sve starts_with, koji simbol sad obradujem, s kim sam pozvao, koje sam sve dubine dosegao, produkcije
def startsWith(SW, symbol, original, whoCalled, productions):

    if symbol == '$':
        return
    if symbol[0] != '<': # epsilone cemo posebno dodavati
        SW[original].add(symbol)
    else:
        for a in productions[symbol]:
            #print ("a ", a[0])
            if a[0] in whoCalled:
                return
            whoCalled.add(symbol)
            startsWith(SW, a[0], original, whoCalled, productions)

#ovdje ce productions biti kopija originalne mape produkcija da se mijenja
def give_epsilons(productions, iduEpsilon):

    for substitution in list(iduEpsilon):
        for key in productions:

            skip = False

            if key in iduEpsilon:
                continue
            listOfLeftSides = productions[key]
            newListOfLeftSides = []
            for leftSide in listOfLeftSides:
                currLeft = leftSide
                if substitution in leftSide:
                    currLeft = [x for x in leftSide if x != substitution]
                    if len(currLeft) == 0:
                        iduEpsilon.add(key)
                        skip = True
                        break

                #nismo breakali => samo stavimo
                newListOfLeftSides.append(currLeft)
            if skip:
                continue
            productions[key] = newListOfLeftSides
            # za dani kljuc koji jos nije u idu epsilon stavljamo nova stanja
# ako se promijenila duljina iduEpsilon onda pozivamo jos koji put




# e sad imamo tko s kim pocinje direktno, ali problem su epsiloni, pa mozda
# nesto pocinje i s onim s cime direktno ne pocinje
# kreiramo mapu produkcije SW2 koje ima produkcije s direktnim epsilonima u sebi (osim epsilona u epsilon)
# SW ne mijenjamo, dakle mogu direktno doci do epsilona te it SW2, to je bitno jedino
# ovo sad sigurno treba pozvat 2 puta ali vise od toga je upitno????, ne znam

def startsWithEpsilons(SW, P, iduEpsilon):

    while True:
        napravio = False

        for key in SW:
            for listOfLeftSides in P[key]:
                for leftSide in listOfLeftSides:
                     i = 0
                     for letter in leftSide:
                        if i == 0:
                            i+=1
                            continue # to smo izracunali prije
                        if letter in iduEpsilon: # kao kljuc zapocinje epsilonom
                            l1 = len(SW[key])
                            SW[key] = SW[key] | SW[letter]
                            l2 = len(SW[key])
                            if l1 != l2:
                                napravio = True
                        else:
                            break
                        #i+=1

        if napravio == False:
            break


lines = (line.rstrip() for line in fileinput.input())

V = next(lines).split()[1:]
start_symbol = V[0]
print (start_symbol)
V = set(V)
T = set(next(lines).split()[1:])
Syn = set(next(lines).split()[1:])
P = defaultdict(list)

vv = None
for line in lines:
    if line[0] == " ":
        P[vv].append(line.split())
    else:
        vv = line

SW = {}
V.add('%')
P['%'] = [[start_symbol]]

for el in V:
    SW[el] = set()

iduEpsilon = set()
for key in P:
    for leftSides in P[key]:
        for leftSide in leftSides:
             if leftSide == '$':
                iduEpsilon.add(key)
                break

#print("iduEpsilon", iduEpsilon)
if len(iduEpsilon) > 0:
    T.add('$') # mislim da to treba

productions = {}
for key in P:
    productions[key] = P[key]

pocSize = len(iduEpsilon)

while True:
    give_epsilons(productions, iduEpsilon)
    novaLen = len(iduEpsilon)
    if novaLen == pocSize:
        break
    pocSize = novaLen


for key in SW:
    for leftSides in P[key]:
        #print ("ls ", leftSides)
        startsWith(SW, leftSides[0], key, set(), P)


startsWithEpsilons(SW, P, iduEpsilon)

for el in iduEpsilon:
    SW[el].add('$')

for el in T:
    SW[el] = [el]
    SW ['$'] = ['$']

print("nezavrsni ", V)
print("terminali ", T)
print("sinkronizacija ", Syn)
print ("produkcije: ", P)
print ("starts_with: ", SW)


#SW2 = {key : list(startsWith(key)) for key in V}
#SW = SW1 + SW2
#dodajem jos dodatnu produkciju <X>
#V.add('<X>')
#P['<X>'] = [[V[0]]]
#SW['<X>'] = SW[V[0]]

#print(json.dumps(P, sort_keys=True, indent=4, separators=(',', ': ')))
#print(json.dumps(SW, sort_keys=True, indent=4, separators=(',', ': ')))
