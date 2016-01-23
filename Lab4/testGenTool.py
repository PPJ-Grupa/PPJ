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
        f = Function("F_MAIN", P.globals)
        f.setReturnConstant(31)
        P.addFunction(f)
        self.helper(P, 31)

    def test_example02(self):
        P = Program("ex2")
        P.defineGlobal("x", 42)

        f = Function("F_MAIN", P.globals)
        f.setReturnVariable("x")
        P.addFunction(f)
        self.helper(P, 42)

    def test_example03(self):
        P = Program("ex3")
        f = Function("F_MAIN", P.globals)
        f.setReturnConstant(1234567890)
        P.addFunction(f)
        self.helper(P, 1234567890)

    def test_example05(self):
        P = Program("ex5")
        P.defineGlobal("x", 15)
        P.defineGlobal("y", 16)

        f = Function("F_MAIN", P.globals)
        f.assignAdd("x", "y")
        P.addFunction(f)
        self.helper(P, 31)

if __name__ == '__main__':
    unittest.main()
