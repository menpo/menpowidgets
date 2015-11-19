from struct import pack as struct_pack


def lists_are_the_same(a, b):
    r"""
    Function that checks if two `lists` have the same elements in the same
    order.

    Returns
    -------
    _lists_are_the_same : `bool`
        ``True`` if the lists are the same.
    """
    if len(a) == len(b):
        for i, j in zip(a, b):
            if i != j:
                return False
        return True
    else:
        return False


def rgb2hex(rgb):
    return unicode('#' + struct_pack('BBB',*rgb).encode('hex'))


def decode_colour(colour):
    if not (isinstance(colour, str) or isinstance(colour, unicode)):
        # we assume that RGB was passed in. Convert it to unicode hex
        return rgb2hex(colour)
    else:
        return unicode(colour)
