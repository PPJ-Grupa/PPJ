import pickle
class DKAState:
    def __init__ (self, num, listOfNDKAs):
        self.num = num
        self.listOfNDKAs = listOfNDKAs # to je lista onih smecara koji su bas ovo samo stanje
        self.dict = {}# mozda preko num-a
        self.states = [] # e to je sad lista onih normalnih

        #pozivat tek kad smo gotovi s konstrukcijom
    def giveRealStates(self):
        for NDKA in self.listOfNDKAs:
            for state in NDKA.states:
                self.states.append(state)

    def add_neighbour(self, letter, state):
        self.dict[letter] = state #number

    def getNeighbour (self, letter):
        if letter in self.dict:
            return self.dict[letter]
        else:
            return -1





class NDKAState:
    def __init__ (self, num):
        self.num = num
        self.dict = {} #neighbours preko A do stanja 2 npr.
        self.states = []
    def addNeighbour(self, letter, state):
        # if it is nka can have more neighbours under same key (unfortionately)
        if letter in self.dict:
            self.dict[letter].append(state)
        else:
            self.dict[letter] = []
            self.dict[letter].append(state)

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
        self.neighbour2 = -1
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


class MakeProductions:

    def __init__ (self, productions, starts_with, zavrsni, nezavrsni, iduEpsilon, pocetnoStanje):
        self.iduEpsilon = iduEpsilon
        self.allEpsilons = set()
        self.listOfStates = []
        self.pozvaniHash = set()
      #  self.dictionaryOfStates = {}
        self.mapaSvih = {}
        self.num = 0
        self.productions = productions
        self.starts_with = starts_with
        self.zavrsni = zavrsni
        self.nezavrsni = nezavrsni
        self.pocetnoStanje = pocetnoStanje
        self.info_production = {} # for production and pointer gives equivalent state number,
        self.call_productions() #dakle rijesili smo konstrukciju u konstruktoru
        self.listOfNDKAStates = []
        self.listOfDKAStates = []
        self.firstState = self.listOfStates[0]
        self.mapaSvih[(self.firstState, str(self.firstState.stavke))] = 0
        self.reverseMap = []
        self.reverseMap.append(self.firstState)
        self.add_epsilon_transformations(self.firstState)
        self.convert_to_NDKA()
        self.convert_to_DKA()
        self.finalTable = {}
        #self.give_table_from_DKAStates()


    def __str__(self):
         return "foo"

    def stateFromProduction(self, production, pointer):

        state = State (production, pointer, self.num)
        if self.num == 0:
            state.stavke.add('$')
        stringDesneStrane = ''.join(production[1])
        stringLijeveStrane = production[0]

        #no point in this epislon transition
        if stringDesneStrane == '$' and pointer == 1:
            return
        if pointer == 0:
            self.info_production[(stringLijeveStrane, stringDesneStrane)] = {pointer : self.num}

       # self.dictionaryOfStates[self.num] = state
        self.listOfStates.append(state)
        self.num+=1


    def call_productions(self):
        production = self.pocetnoStanje
        for rightSide in self.productions[production]:
                for i in range(len(rightSide) + 1):
                     self.stateFromProduction((production, rightSide), i)
        for production in self.productions:
            if production == self.pocetnoStanje:
                continue
            for rightSide in self.productions[production]:
                for i in range(len(rightSide) + 1):
                     self.stateFromProduction((production, rightSide), i)
       # print(len(self.listOfStates))

    def sequence_starts_with(self, sequence, empty_symbols ):

         result = set()
         for symbol in sequence:
            result |= self.starts_with[ symbol ]
            if symbol not in empty_symbols:
                break
         return result

    # pocetno stanje s dodanom stavkom {$}
    def add_epsilon_transformations(self, state):
            #print(len(self.mapaSvih))
            #print ("tu")
            hash1 = (state.num, str(sorted(state.stavke)))
            if hash1 in self.pozvaniHash:
                return
            else:
                self.pozvaniHash.add(hash1)
            myrightSide = state.production[1]
            if state.pointer == len(myrightSide):
                return # ovi nemaju kud dalje
            letter = myrightSide[state.pointer]
            #if state.num == 0:
               # state.stavke.add('$')

            if (letter == '$'):
                return

            #print (letter)

            moze = True
            pocetci = set()
            if state.pointer + 1 == len(myrightSide):
                 pass
            else :
                pocetci |= self.sequence_starts_with(myrightSide[state.pointer+1:], self.starts_with)

            for broj in range(state.pointer+1, len(myrightSide)):
                if not(myrightSide[broj] in self.iduEpsilon):
                     moze = False

            if moze:
                    pocetci|=state.stavke

            if letter in self.productions:


                for rightSide in self.productions[letter]:
                    brightSide = ''.join(rightSide)
                    # debug print (state.num,  self.info_production[brightSide][0])
                    # za svaku desnu stranu
                    curr_neighnour = self.info_production[(letter, brightSide)][0]

                    susjed = self.listOfStates [curr_neighnour]
                    # production, pointer, num
                    #print ("point ", susjed.pointer)
                    noviState = State(susjed.production, susjed.pointer, susjed.num)
                    noviState.neighbour = susjed.get_direct_neighbour()
                    noviState.stavke = set(pocetci)

                    hash1 = (noviState.num, str(sorted(noviState.stavke)))

                    # s tim da u mapu svih treba ubaciti prvo pocetnog tamo gore negdje
                    if hash1 in self.mapaSvih:
                        broj = self.mapaSvih[hash1]
                    else:
                        broj = len(self.mapaSvih)
                        self.mapaSvih[hash1] = broj
                        self.reverseMap.append(noviState)

                    state.epsilonNeighbours.add(broj) #prije je tu bio broj hehe, a ok
                    self.add_epsilon_transformations(noviState)

                    # self.listOfStates[curr_neighnour].stavke |= set(pocetci) # vec je set
                    # treba izgenerirati wrapper oko tog neighboura s tim stavkama
                    # wrappati self.listOfStates[curr_neighbour]
                    # znaci traba nam mapa u kojoj je kljuc
                    # num od origigi stanja, njegove_generirane stavke, a value on
                    # tako izgeneriramo sva takva stanja i imamo pocetno
                    # krenemo od pocetnog, gledamo kakva sve smeca nastaju
                    # i onda za njih pozovemo i naravno gledamo sto smo sve pozvali
                    # to ponovo ne pozivamo, eh moramo tako

                    #ovo je onaj direktni
            if state.neighbour != -1:
                    susjed =  self.listOfStates[state.neighbour]
                    noviState = State(susjed.production, susjed.pointer, susjed.num)
                    noviState.neighbour = susjed.get_direct_neighbour()
                    noviState.stavke = state.stavke

                    hash1 = (noviState.num, str(sorted(noviState.stavke)))

                    # s tim da u mapu svih treba ubaciti prvo pocetnog tamo gore negdje
                    if hash1 in self.mapaSvih:
                        broj = self.mapaSvih[hash1]
                    else:
                        broj = len(self.mapaSvih)
                        self.mapaSvih[hash1] = broj
                        self.reverseMap.append(noviState)

                    state.neighbour2 = broj #ovo je novi

                    self.add_epsilon_transformations(noviState)
    #pocetno stanje, skup hashanih stanja u kojima je bio
    #def create_new_states_with_links(state, skup):
    # i think i acctually managed to convert it to nka, so everything
    # after we print dka size, this function does not make sense
    # since i forgot it is only nka, not dka
    def convert_to_NDKA(self):

        listOfLists = []
        self.num = len(self.reverseMap) # a eto
      #  print ("ENKA", self.num)

        for i in range(0, self.num):
            self.allEpsilons.add(i)
            self.giveSetOfEpsilons (i)
            noviSet = set()
            noviSet |= self.allEpsilons
            listOfLists.append(noviSet)
            self.allEpsilons.clear()

        size = len(listOfLists)
      #  print ("Tu2")

       # print (listOfLists)

        listOfLists = sorted(listOfLists, key = lambda x : len( x ) )


       # print("krafna")

        totalListOfLists = []
        for i in range(0, size):
            bool1 = True
            for j in range(i+1, size):
                if (listOfLists[i].issubset(listOfLists[j])):
                    bool1 = False
                    break
            if bool1:
                totalListOfLists.append( listOfLists[i] )

        numberOfStates = len(totalListOfLists)

      #  print ("tu si")
        # print (totalListOfLists)


        # samo zelimo da nam je pocetno stanje prvo u finalListOfLists
        finalListOfLists = []
        koji = -1
        for i in range(0, numberOfStates):
            # to je start stanje
            if 0 in totalListOfLists[i]:
                koji = i
                finalListOfLists.append(totalListOfLists[i])
                break
        for i in range(0, numberOfStates):
            if i != koji:
                finalListOfLists.append(totalListOfLists[i])

       # print(finalListOfLists)

       # print ("tu si2")
        for i in range(numberOfStates):
            self.listOfNDKAStates.append(NDKAState(i))



        diIdu={}
        for i in range(self.num):
            j = 0
            for lista in finalListOfLists:
                if i in lista:
                    if i in diIdu:
                        diIdu[i].append(j)
                    else:
                        diIdu[i] = [j]

                j+=1


        i = 0
        for lista in finalListOfLists:
            for state in lista:
                statet = self.reverseMap[state]
                self.listOfNDKAStates[i].addState(statet)
                neighbour = statet.neighbour2
                letter = statet.get_letter()
               # print ("tu", statet.production[0], statet.production[1], statet.pointer, neighbour)
                if neighbour != -1:
                    #print (i+1), tu je bilo nezgodno skuzit da treba po svima
                    for el in diIdu[neighbour]:
                        self.listOfNDKAStates[i].addNeighbour(letter, el)
                            #print ("gore", i, letter, j)

            i+=1
      #  print("Tu4")



        #ok sad smo mergali stanja, samo treba jos prijelaze lijepo definirat, hehe..


    #state je integer
    def giveSetOfEpsilons(self, state):
        size = len(self.allEpsilons)
        for num in self.reverseMap[state].epsilonNeighbours:
            self.allEpsilons.add(num)
        #we look if size has changed
        if size == len(self.allEpsilons):
            return

        for num in self.reverseMap[state].epsilonNeighbours:
            if num == state:
                continue
            self.giveSetOfEpsilons(num)


    # ajmo probat pseudokod
        #znamo da krecemo iz prvog samo je on bitan
     #  idemo po stanjima i sad sto, ako za neki znak ima dva ili vise
    # tada ako su to razlicita stanja obv., treba kreirati merge_stanje
    # obradili smo stanje, imamo trenutnu listu listu stanja u koja se vec nekako preslo
    # dakle treba nam pomocna fja koja prima listu stanja i vraca
    # listu_listu stanja u koje je doticno smece preslo
    # u trenutku kada funkcija vrati praznu listu (nema prijelaza jbga) -> gotovi smo
    def convert_to_DKA(self):
      #  print("Tu5")
        queue = []
        firstDKAState = DKAState(0, [self.listOfNDKAStates[0]])
        queue.append(firstDKAState) #stanje DKA je lista NDKA stanja

        self.listOfDKAStates.append(firstDKAState) #hm, preko indeksa mozda bolje
        listOfStateSets = []
        listOfStateSets.append(set([0]))
        num = 0
        while len(queue) != 0:

            trenutni = queue[0]
            returnMap = self.giveMapOfDKAStates(trenutni.listOfNDKAs)
            queue = queue[1:]

            for key in returnMap:
                #print (num)
                listaPov = returnMap[key] #zapravoset
                if listaPov in listOfStateSets:
                    index = listOfStateSets.index(listaPov)
                    trenutni.add_neighbour(key, index)
                    continue

                listOfStateSets.append(listaPov)
                lista = []
                for i in list(listaPov):
                    lista.append(self.listOfNDKAStates[i])
                num+=1
                noviDKAState = DKAState(num, lista)
                trenutni.add_neighbour(key, num)
                self.listOfDKAStates.append(noviDKAState)
                queue.append(noviDKAState)

        #we finish dka definition
        for myDKAState in self.listOfDKAStates:
            myDKAState.giveRealStates()
        #print("Tu6")

      #  print ("DKAka", len(self.listOfDKAStates))



   #gives transitions to NDKA states {1:{q1,q2}}, ali s brojevima !!
    def giveMapOfDKAStates (self, listOfNDKAStates):
        returnMap = {}
        for ndkaState in listOfNDKAStates:
            for key in ndkaState.dict:
                if key in returnMap:
                    returnMap[key].extend(ndkaState.dict[key])
                else:
                    returnMap[key] = []
                    returnMap[key].extend(ndkaState.dict[key])

        for key in returnMap:
            lista = returnMap[key]
            lista = set(lista)
            returnMap[key] = lista

        return returnMap






    def give_table_from_DKAStates(self):
        for i in range(len(self.listOfDKAStates)):
            self.finalTable[i] = {}
        i = 0
        for dkaState in self.listOfDKAStates:
            for state in dkaState.states:



                if state.pointer == len(state.production[1]) and state.production[0] == self.pocetnoStanje:
                    #treba jos provjerit da je zavrsni negdje nesto

                    self.finalTable[i]['$'] = ("A") #kao prihvati
                elif state.production[1][0] == '$' or state.pointer == len(state.production[1]):

                    for stavka in state.stavke:
                         # print ("stavka", stavka)
                        self.finalTable[i][stavka] = ("R",
                        0 if state.production[1][0] == '$' else len(state.production[1]), state.production[0])

                elif state.pointer != len(state.production[1]):

                    letter = state.get_letter()
                    next_state = dkaState.getNeighbour(letter) # ovo tu mi se mora dobro racunat za
                    #fiksno slovo

                    if next_state != -1:
                        if letter in self.zavrsni: # ovo je prema onom u SA redundantno, al eto
                            self.finalTable[i][letter] = ("S", next_state)
                        elif letter in self.nezavrsni:
                            self.finalTable[i][letter] = ("G", next_state)


            i+=1
        return self.finalTable





## S -> AA
## A -> aA | b


#productions = {'%': [['<A>']], '<B>': [['a', '<B>'], ['b']], '<A>': [['<B>', '<A>'], ['$']]}
#starts_with = {'b': ['b'], '$': ['$'], '%': {'$', 'b', 'a'}, '<B>': {'b', 'a'},
#               '<A>': {'$', 'b', 'a'}, 'a': ['a']}


#zavrsni = {'b', 'a', '$'}
#nezavrsni = {'%', '<B>', '<A>'}

#productions = {'<X>':[['<S>']], '<S>':[['<A>', '<A>']], '<A>' : [ ['a', '<A>'], ['b']]}
#starts_with = {'<X>': ['a','b'], '<S>':['a', 'b'], '<A>' : ['a', 'b'], 'a':['a'], 'b':['b'], '$':['$']}
#zavrsni = {'a', 'b', '$'}
#nezavrsni = {'<X>', '<S>', '<A>'}


#maker = MakeProducitons(productions, starts_with, zavrsni, nezavrsni, set() ,'<%>')

"""

definitions = pickle.load( open( 'temporary_definitions.bin', 'rb' ) )

V = definitions['nezavrsni']
T = definitions['terminali']
Syn = definitions['sinkronizacija']
P = definitions['produkcije']
SW = definitions['starts_with']
iduEpsilon = definitions['iduEpsilon']
maker =MakeProductions(P, SW, T, V, iduEpsilon, '<%>')
#maker =  MakeProductions(P, SW, T, V, '<%>')
LRTable = maker.give_table_from_DKAStates()


pickle.dump( LRTable, open( 'x.bin', 'wb' ) )

"""