import fileinput
import json
import copy

from helpers import calculate_padding
from SemantickiAnalizator import SemantickiAnalizator

lines = []
# Remove trailing whitespace from rows
[lines.append(line.rstrip()) for line in fileinput.input()]

#print("\n".join(lines))

# Turn padding into preceding number
lines = [str(calculate_padding(line)) + ' ' + line.lstrip() for line in lines]
# Revere list for pop() to remove the first element
#lines = list(reversed(lines))
#[print(line) for line in lines]

""" Start propagation """
semanticki_analizator = SemantickiAnalizator(lines)
semanticki_analizator.start()
