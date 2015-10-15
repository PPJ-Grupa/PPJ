import pickle

from regex import *

if __name__ == '__main__':
    transitions = pickle.load( open( 'temporary_definitions.bin', 'rb' ) )
    print( transitions )
