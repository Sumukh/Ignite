def ceildiv(a, b):
    return -(-a // b)

def chunks(l, n):
    """ Divides L into N many chunks, each containing approximately the
    same number of elements
    Refrence: http://stackoverflow.com/a/9873935
    >>> [len(x) for x in chunks(range(45), 13)]
    [4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 4, 3, 3]
    >>> [len(x) for x in chunks(range(253), 13)]
    [20, 19, 20, 19, 20, 19, 20, 19, 20, 19, 20, 19, 19]
    >>> [len(i) for i in chunks(range(56), 3)]
    [19, 19, 18]
    >>> [len(i) for i in chunks(range(55), 5)]
    [11, 11, 11, 11, 11]
    """
    length = len(l)
    prev_index = 0
    for i in range(1, n + 1):
        index = ceildiv(i * length, n)
        yield l[prev_index:index]
        prev_index = index
