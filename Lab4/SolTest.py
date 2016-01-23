__author__ = 'Mihael'
import fileinput
import json
import copy
import sys
import os

from FinalCodeGenerator import *

#lines = []
# Remove trailing whitespace from rows

#print("\n".join(lines))

# Revere list for pop() to remove the first element
#lines = list(reversed(lines))
#[print(line) for line in lines]
print (os.getcwd())
path = os.getcwd() + "/4labos-2012-2012/09_bitand/test.in"
print(path)

lines = open(path).readlines()

""" Start propagation """
semanticki_analizator = SemantickiAnalizator(lines)
result = semanticki_analizator.parse()
print(result)
