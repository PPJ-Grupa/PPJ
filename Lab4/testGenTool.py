import unittest
import sh
from GenerationToolbox import *


class TestStringMethods(unittest.TestCase):

    def helper(self, program, output):
        fname = getattr(program, "name", "a") + ".frisc"
        with open(fname, "w") as f:
            f.write(str(program))
            f.close()
            res = sh.nodejs("FRISCjs/consoleapp/frisc-console.js", fname)
            res = int(res)
            self.assertEqual(res, output)

    def test_integration(self):
        self.helper("\n".join(["    MOVE %D 42, R6", "    HALT"]), 42)

    def test_example_1(self):
        P = Program("ex1")
        f = Function("MAIN", P.globals)
        f.setReturnConstant(31)
        P.addFunction(f)
        self.helper(P, 31)

    def test_example02(self):
        P = Program("ex2")
        P.defineGlobal("x", 42)

        f = Function("MAIN", P.globals)
        f.setReturnVariable("x")
        P.addFunction(f)
        self.helper(P, 42)

    def test_example03(self):
        P = Program("ex3")
        f = Function("MAIN", P.globals)
        f.setReturnConstant(1234567890)
        P.addFunction(f)
        self.helper(P, 1234567890)

    def test_ex4(self):
        P = Program("ex4")
        f = Function("MAIN", P.globals)
        f.setReturnConstant(-84)
        P.addFunction(f)
        self.helper(P, -84)

    def test_example05(self):
        P = Program("ex5")
        P.defineGlobal("x", 15)
        P.defineGlobal("y", 16)

        f = Function("MAIN", P.globals)
        f.assignAdd("x", "y")
        P.addFunction(f)
        self.helper(P, 31)

    def test_ex11(self):
        P = Program("ex11")
        f = Function("F", P.globals)
        f.setReturnConstant(123)

        main = Function("MAIN", P.globals)
        main.assignFunc(f, [])

        P.addFunction(f)
        P.addFunction(main)
        self.helper(P, 123)

    def test_ex12(self):
        P = Program("ex12")
        f = Function("f", P.globals, ["x"])
        f.assignAdd("x", 5)

        main = Function("main", P.globals)
        main.assignFunc(f, [7])

        P.addFunction(f)
        P.addFunction(main)
        self.helper(P, 12)

    def test_2paramf(self):
        P = Program("2paramf")
        f = Function("f", P.globals, ["x", "y", "z"])
        f.assignAdd("x", "y")

        main = Function("main", P.globals)
        main.assignFunc(f, [7, 5, 100])

        P.addFunction(f)
        P.addFunction(main)
        self.helper(P, 12)

    def test_ex13(self):
        P = Program("ex13")
        f = Function("f", P.globals, ["x"])
        f.assignAdd("x", 5)

        main = Function("main", P.globals)
        main.defVariable("tmp0")
        main.defVariable("tmp1")
        main.assignFunc(f, [7], "tmp0")
        main.assignFunc(f, [-4], "tmp1")
        main.assignAdd("tmp0", "tmp1")

        P.addFunction(f)
        P.addFunction(main)
        self.helper(P, 13)

if __name__ == '__main__':
    unittest.main()
