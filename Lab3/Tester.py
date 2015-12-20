import fileinput
import os
from MojSemantickiAnalizator import SemantickiAnalizator

def getf(getFile, fromWhere):
  return [ fromWhere + '\\' + file for file in os.listdir(fromWhere) if getFile == ('.' in file)]

testsFolder = [ folder for folder in getf(False, os.getcwd()) if not '__' in folder ][0]
print(testsFolder)

for i, folder in enumerate(getf(False, testsFolder)):
  files = getf(True, folder)
  inFile = open([ file for file in files if '.in' in file ][0]).readlines()
  #print(inFile)
  outFile = open([ file for file in files if '.out' in file ][0]).read()
  resultFromIn = SemantickiAnalizator(inFile).parse() + "\n"
  if not resultFromIn == outFile:
    print("######################################")
    print(i+1)
    print("dobiveno:")
    print(resultFromIn)
    print("ocekivano:")
    print(outFile)
    print(str(resultFromIn == outFile))