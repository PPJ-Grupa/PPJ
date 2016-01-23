from collections import ChainMap


class Instruction():
    def __init__(self, cmd, label=""):
        self.cmd = cmd
        self.label = label

    def __str__(self):
        return "%s %s" % (self.label.ljust(15), self.cmd)


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

    class LocalVariable():
        def __init__(self, name, context, offset=0):
            assert hasattr(context, 'offset')
            self.context = context
            self.offset = offset
            self.name = name

        def load(self, reg):
            return [Instruction("LOAD %s, (R7 + 0%X)" % (reg, self.offset + self.context.offset))]

        def save(self, reg):
            return [Instruction("LOAD %s, (R7 + 0%X)" % (reg, self.offset + self.context.offset))]

    def __init__(self, name, outer_variable, params=[]):
        self.name = name
        self.label = "F_" + name.upper()
        self.constants = set()
        self.variable = ChainMap(dict(), outer_variable)
        self.instuctions = []
        self.__saveContext()
        self.offset = 0

        for i, var in enumerate(params):
            self.variable[var] = self.LocalVariable(var, self, i * 4 + 24)

    def defVariable(self, name):
        self.offset += 4
        self.instuctions.append(Instruction("SUB R7, 4, R7"))
        self.variable[name] = self.LocalVariable(name, self, -self.offset)

    def __saveContext(self):
        for i in range(1, 6):
            self.instuctions.append(Instruction("PUSH R%d" % i))

    def __return(self):
        for i in range(5, 0, -1):
            self.instuctions.append(Instruction("POP R%d" % i))
        self.instuctions.append(Instruction("RET"))

    def __loadInto(self, value, reg):
        if type(value) == int:  # constant
            self.constants.add(value)
            self.instuctions.append(Instruction("LOAD %s, (C_%d)" % (reg, value)))
        elif type(value) == str:  # var name
            self.instuctions.extend(self.variable[value].load(reg))
        else:
            raise NotImplemented

    def setReturnConstant(self, value):
        self.__loadInto(value, "R6")
        self.__return()

    def setReturnVariable(self, name):
        self.__loadInto(name, "R6")
        self.__return()

    def assignBinaryOperation(self, op, a, b, ret=None):
        self.__loadInto(a, "R0")
        self.__loadInto(b, "R1")
        self.instuctions.append(Instruction(op + " R0, R1, R6"))
        if ret is not None:
            self.instuctions.extend(self.variable[ret].save("R6"))

    def assignAdd(self, a, b, ret=None):
        self.assignBinaryOperation("ADD", a, b, ret)

    def assignFunc(self, f, args, ret=None):
        for arg in reversed(args):
            self.__loadInto(arg, "R0")
            self.instuctions.append(Instruction("PUSH R0"))
        self.instuctions.append(Instruction("CALL " + f.label))
        if ret is not None:
            self.instuctions.extend(self.variable[ret].save("R6"))
        self.instuctions.append(Instruction("ADD R7, 0%X, R7" % (len(args) * 4)))

    def __frisc__(self):
        code = self.instuctions

        if len(code) == 0 or code[-1].cmd != "RET":  # Preventing duplicate RET
            self.__return()
            code = self.instuctions

        for c in self.constants:
            code.append(Instruction("DW %%D %d" % c, label="C_" + str(c)))

        code[0].label = self.label
        return code


class Program:
    def __init__(self, name=""):
        self.functions = set()
        self.globals = dict()
        self.name = name

    def addFunction(self, f):
        self.functions.add(f)

    def defineGlobal(self, name, init=0):
        self.globals[name] = GlobalVariable(name, init)

    def __frisc__(self):
        output = []
        output.append(Instruction("MOVE 40000, R7"))
        output.append(Instruction("CALL F_MAIN"))
        output.append(Instruction("HALT"))

        for g in self.globals.values():
            output.extend(g.__frisc__())

        for f in self.functions:
            output.extend(f.__frisc__())
        return output

    def __str__(self):
        return "\n".join(str(x) for x in self.__frisc__())
