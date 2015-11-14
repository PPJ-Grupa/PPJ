__author__ = 'Mihael'
import copy
#ona prosirenja za lr1 parser nisu ni pokusana biti implementirana (stavke {a,b})

#after we bild e-nka, then dka should come
class DKAState:
    def __init__ (self, num):
        self.num = num
        self.dict = {} #neighbours preko A do stanja 2 npr.
        self.states = []
    def addNeighbour(self, letter, state):
        # if it is nka can have more neighbours under same key (unfortionately)
        self.dict[letter] = state

    def getNeighbour (self, letter):
        if letter in self.dict:
            return self.dict[letter]
        else:
            return -1


    def addState(self, state):
        self.states.append(state)


#grammar, kraj niza ~
#e - automat je definiran s
# (produkcija, [lista zapoinje znakova])
# produkcija je uredeni par doista produkcije i integera (pointera na mjestu u prodkucji)
# za svako stanje automata postoji lista  prijelaza
#tocka je pointer
#treba mi za svaku lijevu stranu odgovor na upit ima li epsilon prijelaz, zapravo starts_with, ok

class State:
    def __init__(self, production, pointer, num):
        self.num = num # broj 0,1, koje stanje po redu
        self.production = production # tuple (A, abc) ako A->abc
        self.pointer = pointer
        self.stavke = set() # one stavke tipa {a, b}
        self.neighbour = -1
        self.productionLength = len(production[1])
        self.epsilonNeighbours = set()
        self.add_direct_neighbour()


    def add_direct_neighbour(self):
        #dodajemo direktnog osim ak nije epsilon prijelaz u pitanju
        if self.pointer != self.productionLength and not(self.production[1][0] == '$'):
            self.neighbour = self.num + 1

    def get_direct_neighbour(self):
        return self.neighbour

    def get_letter(self):
        if self.neighbour == -1:
            return "~" #ugl nije
        else:
            return self.production[1][self.pointer]


class MakeProducitons:

    def __init__ (self, productions, starts_with, zavrsni, nezavrsni, pocetnoStanje):
        self.allEpsilons = set()
        self.listOfStates = []
        self.dictionaryOfStates = {}
        self.num = 0
        self.productions = productions
        self.starts_with = starts_with
        self.zavrsni = zavrsni
        self.nezavrsni = nezavrsni
        self.pocetnoStanje = pocetnoStanje
        self.info_production = {} # for production and pointer gives equivalent state number,
        self.call_producitons() #dakle rijesili smo konstrukciju u konstruktoru
        self.listOfDKAStates = []
        self.add_epsilon_transformations()
        self.add_missing_stavke() # poslijedica toga da nemamo one s direktnim prijelazima stavke popunjene
        self.convert_to_DKA()
        self.finalTable = {}
        self.give_table_from_DKAStates()


    def __str__(self):
         return "foo"

    def stateFromProduciton(self, production, pointer):

        state = State (production, pointer, self.num)
        stringDesneStrane = ''.join(production[1])
        stringLijeveStrane = production[0]

        #no point in this epislon transition
        if stringDesneStrane == '$' and pointer == 1:
            return
        # debug print ("start", stringDesneStrane, pointer, self.num)
        if pointer == 0:
            self.info_production[(stringLijeveStrane, stringDesneStrane)] = {pointer : self.num}

        self.dictionaryOfStates[self.num] = state
        self.listOfStates.append(state)
        self.num+=1


    def call_producitons(self):
        production = self.pocetnoStanje
        for rightSide in self.productions[production]:
                for i in range(len(rightSide) + 1):
                     self.stateFromProduciton((production, rightSide), i)
        for production in self.productions:
            if production == self.pocetnoStanje:
                continue
            for rightSide in self.productions[production]:
                for i in range(len(rightSide) + 1):
                     self.stateFromProduciton((production, rightSide), i)


    def add_epsilon_transformations(self):
        for state in self.listOfStates:
            myrightSide = state.production[1]
            if state.pointer == len(myrightSide):
                continue
            letter = myrightSide[state.pointer]

            if state.num == 0:
                state.stavke.add('$')

            if letter in self.productions:

                if state.pointer + 1 == len(myrightSide):
                   prvi_znak_od_zapocinje = '$'
                else:
                    prvi_znak_od_zapocinje = myrightSide[state.pointer + 1]

                pocetci = self.starts_with[prvi_znak_od_zapocinje]


                for rightSide in self.productions[letter]:
                    brightSide = ''.join(rightSide)
                    # debug print (state.num,  self.info_production[brightSide][0])
                    # za svaku desnu stranu
                    curr_neighnour = self.info_production[(letter, brightSide)][0]
                    self.listOfStates[curr_neighnour].stavke |= set(pocetci)
                    state.epsilonNeighbours.add(curr_neighnour)

    def add_missing_stavke(self):
        for state in self.listOfStates:
            if state.neighbour != -1:
                self.listOfStates[state.neighbour].stavke |= state.stavke


    # i think i acctually managed to convert it to nka, so everything
    # after we print dka size, this function does not make sense
    # since i forgot it is only nka, not dka
    def convert_to_DKA(self):
        listOfLists = []

        for i in range(0, self.num):
            self.allEpsilons.add(i)
           # print ("eps", i, self.listOfStates[i].epsilonNeighbours)
            self.giveSetOfEpsilons (i)
          #  print (setOfEpsilons)
            noviSet = set()
            noviSet |= self.allEpsilons
            # print (noviSet)
            listOfLists.append(noviSet)
            self.allEpsilons.clear()

        size = len(listOfLists)
        print("ENKA", size)


        for i in range(0, size):
            for j in range(i+1, size):
                if len(listOfLists[i]) > len(listOfLists[j]):
                    prviS = set(listOfLists[i])
                    listOfLists[i] = set(listOfLists[j])
                    listOfLists[j] = prviS

        totalListOfLists = []
        for i in range(0, size):
            bool = True
            for j in range(i+1, size):
                if (listOfLists[i].issubset(listOfLists[j])):
                    bool = False
                    break
            if bool:
                totalListOfLists.append( list (listOfLists[i]) )

        numberOfStates = len(totalListOfLists)
        # print (totalListOfLists)


        # samo zelimo da nam je pocetno stanje prvo u finalListOfLists
        finalListOfLists = []
        koji = -1
        for i in range(0, numberOfStates):
            # to je start stanje
            if 0 in totalListOfLists[i]:
                koji = i
                finalListOfLists.append(list(totalListOfLists[i]))
                break
        for i in range(0, numberOfStates):
            if i != koji:
                finalListOfLists.append(list(totalListOfLists[i]))


       # print (finalListOfLists)
        print ("DKA", numberOfStates)

        for i in range(numberOfStates):
            self.listOfDKAStates.append(DKAState(i))

        i = 0
        for lista in finalListOfLists:
            for state in lista:
                statet = self.listOfStates[state]
                self.listOfDKAStates[i].addState(statet)
                neighbour = statet.get_direct_neighbour()
                letter = statet.get_letter()
               # print ("tu", statet.production[0], statet.production[1], statet.pointer, neighbour)
                if neighbour != -1:
                    #print (i+1), tu je bilo nezgodno skuzit da treba po svima
                    for j in range(0, numberOfStates):
                        otherList = finalListOfLists[j]
                        if neighbour in otherList:
                            self.listOfDKAStates[i].addNeighbour(letter, j)
                            #print ("gore", i, letter, j)

            i+=1



        #ok sad smo mergali stanja, samo treba jos prijelaze lijepo definirat, hehe..


    #state je integer
    def giveSetOfEpsilons(self, state):
        size = len(self.allEpsilons)
        for num in self.listOfStates[state].epsilonNeighbours:
            self.allEpsilons.add(num)
        #we look if size has changed
        if size == len(self.allEpsilons):
            return

        for num in self.listOfStates[state].epsilonNeighbours:
            if num == state:
                continue
            self.giveSetOfEpsilons(num)


    def give_table_from_DKAStates(self):
        for i in range(len(self.listOfDKAStates)):
            self.finalTable[i] = {}
        i = 0
        for dkaState in self.listOfDKAStates:
            for state in dkaState.states:

                if state.pointer == len(state.production[1]) and state.production[0] == self.pocetnoStanje:
                    #treba jos provjerit da je zavrsni negdje nesto
                    #
                    # print ("pocetno_prihvatam")
                    self.finalTable[i]['$'] = ("A") #kao prihvati
                elif state.production[1][0] == '$' or state.pointer == len(state.production[1]):
                    j=0
                    for stavka in state.stavke:
                         self.finalTable[i][stavka] = ("R",
                         0 if state.production[1][0] == '$' else len(state.production[1]), state.production[0])
                         j+=1
                elif state.pointer != len(state.production[1]):
                    letter = state.get_letter()
                    next_state = dkaState.getNeighbour(letter)

                    if next_state != -1:
                        if letter in self.zavrsni: # ovo je prema onom u SA redundantno, al eto
                            self.finalTable[i][letter] = ("S", next_state)
                        elif letter in self.nezavrsni:
                            self.finalTable[i][letter] = ("G", next_state)


            i+=1
        print (self.finalTable)









## S -> AA
## A -> aA | b


#productions = {'<S>':[['<A>']], '<A>': [['<B>', '<A>'], ['$']], '<B>': [['a', '<B>'], ['b']]}
#starts_with = {'<B>': ['b', 'a'], '<A>': ['$', 'b', 'a'], '<S>' : ['$', 'b', 'a'],
#              'a' : ['a'], 'b':['b'], '$' : ['$']}

#zavrsni = {'a', 'b', '$'}
#nezavrsni = {'<S>', '<A>', '<B>'}

productions = {'<X>':[['<S>']], '<S>':[['<A>', '<A>']], '<A>' : [ ['a', '<A>'], ['b']]}
starts_with = {'<X>': ['a','b'], '<S>':['a', 'b'], '<A>' : ['a', 'b'], 'a':['a'], 'b':['b'], '$':['$']}
zavrsni = {'a', 'b', '$'}
nezavrsni = {'<X>', '<S>', '<A>'}



maker = MakeProducitons(productions, starts_with, zavrsni, nezavrsni, '<X>')
