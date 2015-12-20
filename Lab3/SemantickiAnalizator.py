import fileinput
import json
import copy

from MojSemantickiAnalizator import SemantickiAnalizator

lines = []
# Remove trailing whitespace from rows

#print("\n".join(lines))

# Revere list for pop() to remove the first element
#lines = list(reversed(lines))
#[print(line) for line in lines]

""" Start propagation """
semanticki_analizator = SemantickiAnalizator(lines)
result = semanticki_analizator.parse()
print(result)
