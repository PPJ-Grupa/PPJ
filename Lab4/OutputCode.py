
class OutputCode:
    ### sigurno treba jos nesto predfinirat
    def __init__(self):
        self.listOfFirstCommands = [] #uvijek tri efektivne naredbe na pocetku

        self.numOfLabels = 0
        self.label = "LABEL"
        self.listOfLabels = []
        self.labels = {} # npr. G_X DW %D 12

        self.listOfFunctions = []
        self.functions = {} # functions[name] = [lista naredbi], lista naredbi za svaku fju

        self.addFirstCommand('MOVE 40000, R7')
        self.addFirstCommand('CALL F_MAIN')
        self.addFirstCommand('HALT')

        # postoji fja imena 'F_MAIN'
        self.listOfFunctions.append('F_MAIN')

        self.takenRegisters = [False for i in range(0, 7)]
        self.registers = { } # kljuc je identifikator, povratna vrijednost je registar u kojem je njegova vrijednost
        #znamo da se povratna vrijednost funkcije uvijek sprema u R6, R7, stog pointer


    def takeRegister (self, idn, registar):
        self.registers[idn] = registar #registar je broj
        self.takenRegisters[registar] = True

    def returnRegister(self):
        for i, el in enumerate(self.takenRegisters):
            if el == False:
                return i
        return None


    def addFirstCommand (self, command):
        self.listOfFirstCommands.append(' ' + command)

    def generateLabel (self, const): #nekaj kaj zapisujemo u labelu, recimo da je za sad `DW unutar toga
        self.numOfLabels+=1
        currLabel = self.label + str(self.numOfLabels)
        self.listOfLabels.append(const) # sadrzaj labele ide u listu labelea
        self.labels[const] = currLabel # labela se dohvaca preko sadrzaja
        return currLabel

    def addCommandToFunction (self, name, command):
        if not name in self.functions:
            self.functions[name] = []
            self.functions[name].append(name)

        self.functions[name].append(' ' + command)

    def functionToString(self, name):
        outFun = ""
        for el in self.functions[name]:
            outFun += el + "\n"

        # ZA SAD tek kad je u string stavljamo dodamo ret
        outFun+=" RET\n"

        return  outFun

    def generateOutputProgramm(self):
        output = ""
        for el in self.listOfFirstCommands:
            output += el + "\n"
        output += "\n"

        for function in self.listOfFunctions:
            outFun = self.functionToString(function)
            output += outFun + "\n"

        for const in self.listOfLabels:
            output += self.labels[const] + " " + const + " \n"

        return output


