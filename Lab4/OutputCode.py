
class OutputCode:
    ### sigurno treba jos nesto predfinirat
    def __init__(self):
        self.listOfFirstCommands = [] #uvijek tri efektivne naredbe na pocetku
        self.labelDefintions = [] # npr. G_X DW %D 12
        self.listOfFunctions = []
        self.functions = {} # functions[name] = [lista naredbi], lista naredbi za svaku fju

        self.addFirstCommand('MOVE 40000, R7')
        self.addFirstCommand('CALL F_MAIN')
        self.addFirstCommand('HALT')

        # postoji fja imena 'F_MAIN'
        self.listOfFunctions.append('F_MAIN')



    def addFirstCommand (self, command):
        self.listOfFirstCommands.append(' ' + command)


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

        return output


