def tail( lst ):
    """Returns a tail of a given list"""
    if not lst: raise IndexError( 'Empty list has no tail' )
    return lst[ 1: ] if len( lst ) > 1 else []
