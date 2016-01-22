from collections import ChainMap


class Instruction():
    def __init__(self, cmd, label=""):
        self.cmd = cmd
        self.label = label

    def __str__(self):
        return "%15s %s" % (self.label, self.cmd)


class Constant():
    def __init__(self, value):
        self.value = value


class Variable():
    def load(self, reg):
        raise NotImplemented

    def save(self, reg):
        raise NotImplemented


class GlobalVariable(Variable):
    def __init__(self, name, init=0):
        self.name = name
        self.init = init

    def load(self, reg):
        return [Instruction("LOAD %s, (G_%s)" % (reg, self.name))]

    def save(self, reg):
        return [Instruction("STORE %s, (G_%s)" % (reg, self.name))]

    def __frisc__(self):
        return [Instruction("DW %%D %d" % self.init, label="G_" + self.name)]


class Function():
    def __init__(self, name, outer_variable):
        self.name = name
        self.constants = set()
        self.variable = ChainMap(dict(), outer_variable)
        self.instuctions = []

    def setReturnConstant(self, value):
        self.constants.add(value)
        self.instuctions.append(Instruction("LOAD R6, (C_%d)" % value))
        self.instuctions.append(Instruction("RET"))

    def setReturnVariable(self, name):
        self.instuctions.extend(self.variable[name].save("R6"))
        self.instuctions.append(Instruction("RET"))

    def __frisc__(self):
        code = self.instuctions

        for c in self.constants:
            code.append(Instruction("DW %%D %d" % c, label="C_" + str(c)))

        code[0].label = self.name
        return code


class Program:
    def __init__(self):
        self.functions = set()
        self.globals = dict()

    def addFunction(self, f):
        self.functions.add(f)

    def defineGlobal(self, name, init=0):
        self.globals[name] = GlobalVariable(name, init)

    def genOutput(self):
        output = []
        output.append(Instruction("MOVE 40000, R7"))
        output.append(Instruction("CALL F_MAIN"))
        output.append(Instruction("HALT"))

        for g in self.globals.values():
            output.extend(g.__frisc__())

        for f in self.functions:
            output.extend(f.__frisc__())
        return "\n".join(str(x) for x in output)


def example01():
    P = Program()
    f = Function("F_MAIN", P.globals)
    f.setReturnConstant(31)
    P.addFunction(f)
    print(P.genOutput())


def example02():
    P = Program()
    P.defineGlobal("x", 42)

    f = Function("F_MAIN", P.globals)
    f.setReturnVariable("x")
    P.addFunction(f)
    print(P.genOutput())


def example03():
    P = Program()
    f = Function("F_MAIN", P.globals)
    f.setReturnConstant(1234567890)
    P.addFunction(f)
    print(P.genOutput())

def example05():
    pass

if __name__ == "__main__":
    example01()
    print("== ex 2 ==")
    example02()
    print("== ex 3 ==")
    example03()
