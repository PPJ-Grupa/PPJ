__author__ = 'Mihael'

#ona prosirenja za lr1 parser nisu ni pokusana biti implementirana (stavke {a,b})

#after we bild e-nka, then dka should come
class DKAState:
    def __init__ (self, num):
        self.num = num
        self.dict = {} #neighbours preko A do stanja 2 npr.
        self.productions = []
    def addNeighbour(self, letter, state):
        self.dict[letter] = state

    def addProduction(self, production):
        self.productions.append(production)


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
        self.epsilonNeighbours = []
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
            return self.production[0]


class MakeProducitons:

    def __init__ (self, productions, starts_with):
        self.listOfStates = []
        self.dictionaryOfStates = {}
        self.num = 0
        self.productions = productions
        self.starts_with = starts_with
        self.info_production = {} # for production and pointer gives equivalent state number,
        self.call_producitons() #dakle rijesili smo konstrukciju u konstruktoru
        self.listOfDKAStates = []
        self.add_epsilon_transformations()
        self.add_missing_stavke() # poslijedica toga da nemamo one s direktnim prijelazima stavke popunjene
        self.convert_to_DKA()


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
        for production in self.productions:
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

                    state.epsilonNeighbours.append(curr_neighnour)

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

            setOfEpsilons = set()
            setOfEpsilons.add(i)
            self.giveSetOfEpsilons (i, setOfEpsilons)
            listOfLists.append(setOfEpsilons)

        size = len(listOfLists)

        print("ENKA", size)

        totalListOfLists = []

        for i in range(0, size):
            for j in range(i+1, size):
                if len(listOfLists[i]) > len(listOfLists[j]):
                    prviS = listOfLists[i]
                    listOfLists[i] = listOfLists[j]
                    listOfLists[j] = prviS

        for i in range(0, size):
            bool = True
            for j in range(i+1, size):
                if (listOfLists[i].issubset(listOfLists[j])):
                    bool = False
                    break
            if bool:
                totalListOfLists.append( list (listOfLists[i]) )

        numberOfStates = len(totalListOfLists)

        print (totalListOfLists)
        print ("DKA", numberOfStates)

        for i in range(numberOfStates):
            self.listOfDKAStates.append(DKAState(i))

        i = 0
        for lista in totalListOfLists:
            for state in lista:
                statet = self.listOfStates[state]
                neighbour = statet.get_direct_neighbour()
                letter = statet.get_letter()
                if neighbour != -1:
                    for j in range(i+1, len(totalListOfLists)):
                        otherList = totalListOfLists[j]
                        if neighbour in otherList:
                            self.listOfDKAStates[i].addNeighbour(letter, j)
            i+=1



        #ok sad smo mergali stanja, samo treba jos prijelaze lijepo definirat, hehe..


    #state je integer
    def giveSetOfEpsilons(self, state, allEpsilons):
        size = len(allEpsilons)
        for num in self.listOfStates[state].epsilonNeighbours:
            allEpsilons.add(num)
        #we look if size has changed
        if size == len(allEpsilons):
            return

        for num in self.listOfStates[state].epsilonNeighbours:
            if num == state:
                continue
            self.giveSetOfEpsilons(num, allEpsilons)











productions = {'<S>':[['<A>']], '<A>': [['<B>', '<A>'], ['$']], '<B>': [['a', '<B>'], ['b']]}
starts_with = {'<B>': ['b', 'a'], '<A>': ['$', 'b', 'a'], '<S>' : ['$', 'b', 'a'],
               'a' : ['a'], 'b':['b'], '$' : ['$']}

maker = MakeProducitons(productions, starts_with)
