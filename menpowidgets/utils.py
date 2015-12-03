from struct import pack as struct_pack
import numpy as np


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
    return str('#' + struct_pack('BBB', *rgb).encode('hex'))


def decode_colour(colour):
    if not (isinstance(colour, str) or isinstance(colour, unicode)):
        # we assume that RGB was passed in. Convert it to unicode hex
        return rgb2hex(colour)
    else:
        return str(colour)


def str_is_int(s):
    r"""
    Function that returns ``True`` if a given `str` is a positive or negative
    integer.

    Parameters
    ----------
    s : `str`
        The command string.
    """
    return s.isdigit() or (s.startswith('-') and s[1:].isdigit())


def str_is_float(s):
    r"""
    Function that returns ``True`` if a given `str` is a positive or negative
    float.

    Parameters
    ----------
    s : `str`
        The command string.
    """
    return s.count(".") == 1 and str_is_int(s.replace('.', '', 1))


def parse_int_range_command_with_comma(cmd):
    r"""
    Function that parses a range/list command for which contains at least one
    comma (``,``). The function returns a `list` with the integer values that
    are included in the command. It also ignores any redundant whitespaces
    that may exist in the command. For example ::

        parse_int_range_command_with_comma([1, 2,-3 ])

    returns ::

        '[1, 2, -3]'

    Parameter
    ---------
    cmd : `str`
        The command string.

    Returns
    -------
    cmd_list : `list`
        The list of integers.

    Raises
    ------
    ValueError
        Command cannot start or end with ','.
    ValueError
        Command cannot contain ',,'.
    ValueError
        Only integers allowed.
    """
    if cmd.startswith(',') or cmd.endswith(','):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(',')
        # for each part
        final_cmd = []
        for i in tmp_cmd:
            if len(i) == 0:
                # this means that there was the ',,' pattern
                raise ValueError("Command cannot contain ',,'.")
            elif str_is_int(i):
                # if it is a positive or negative integer convert it to int
                final_cmd.append(int(i))
            else:
                # else raise an error
                raise ValueError("Only integers allowed.")
        return final_cmd


def parse_int_range_command(cmd):
    r"""
    Function that parses a command for list/range. It is able to recognize any
    pattern and detect pattern errors. Some characteristic examples are "10",
    "[10, 20]", "10, 20", "range(10)", "range(10, 20)", "range(10, 20, 2)",
    "1, 5, -3", etc. The function returns a `list` with integers, after
    interpreting the given command. It also ignores any redundant whitespaces
    that may exist in the command.

    Parameters
    ----------
    cmd : `str`
        The command string.

    Returns
    -------
    cmd_list : `list`
        The list of integers.

    Raises
    ------
    ValueError
        Command cannot contain floats.
    ValueError
        Wrong range command.
    ValueError
        Wrong command.
    """
    # remove all redundant spaces from cmd
    cmd = cmd.replace(" ", "")

    # remove all brackets from cmd
    cmd = cmd.replace("[", "")
    cmd = cmd.replace("]", "")

    # if cmd has '.' then it contains at least a float
    if cmd.count(".") > 0:
        raise ValueError("Command cannot contain floats.")

    # cmd has the form of "range(1, 10, 2)" or "range(10)"
    if cmd.startswith("range("):
        n_comma = cmd.count(",")
        if cmd.endswith(")") and (n_comma == 0 or n_comma == 1 or n_comma == 2):
            return eval(cmd)
        else:
            raise ValueError("Wrong range command.")

    # empty command
    if cmd == "":
        return []

    # get number of ','
    n_comma = cmd.count(",")

    if n_comma > 0:
        # parse cmd given that it contains only ','
        return parse_int_range_command_with_comma(cmd)
    elif n_comma == 0 and str_is_int(cmd):
        # cmd has the form of "10"
        return [int(cmd)]
    else:
        raise ValueError("Wrong command.")


def parse_float_range_command_with_comma(cmd):
    r"""
    Function that parses a range/list command for which contains at least one
    comma (``,``). The function returns a `list` with the float values that
    are included in the command. It also ignores any redundant whitespaces
    that may exist in the command. For example ::

        parse_float_range_command_with_comma([1., 2.,-3.])

    returns ::

        '[1.0, 2.0, -3.0]'

    Parameter
    ---------
    cmd : `str`
        The command string.

    Returns
    -------
    cmd_list : `list`
        The list of floats.

    Raises
    ------
    ValueError
        Command cannot start or end with ','.
    ValueError
        Command cannot contain ',,'.
    ValueError
        Only integers allowed.
    """
    if cmd.startswith(',') or cmd.endswith(','):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(',')
        # for each part
        final_cmd = []
        for i in tmp_cmd:
            if len(i) == 0:
                # this means that there was the ',,' pattern
                raise ValueError("Command cannot contain ',,'.")
            elif str_is_int(i) or str_is_float(i):
                # if it is a positive or negative integer convert it to float
                final_cmd.append(float(i))
            else:
                # else raise an error
                raise ValueError("Only floats allowed.")
        return final_cmd


def parse_float_range_command(cmd):
    r"""
    Function that parses a command for list/range. It is able to recognize any
    pattern and detect pattern errors. Some characteristic examples are "10.5",
    "[10., 20.]", "10., 20.", "range(10.)", "range(10., 20.)",
    "range(10., 20., 2.)", "1., 5., -3.2", etc. The function returns a `list`
    with integers, after interpreting the given command. It also ignores any
    redundant whitespaces that may exist in the command.

    Parameters
    ----------
    cmd : `str`
        The command string.

    Returns
    -------
    cmd_list : `list`
        The list of floats.

    Raises
    ------
    ValueError
        Wrong range command.
    ValueError
        Wrong command.
    """
    # remove all redundant spaces from cmd
    cmd = cmd.replace(" ", "")

    # remove all brackets from cmd
    cmd = cmd.replace("[", "")
    cmd = cmd.replace("]", "")

    # cmd has the form of "range(1, 10, 2)" or "range(10)"
    if cmd.startswith("range("):
        if cmd.endswith(")"):
            nums = cmd[6:-1].split(',')
            if len(nums) == 1:
                arg1 = 0.
                arg2 = float(nums[0])
                arg3 = 1.
            elif len(nums) == 2:
                arg1 = float(nums[0])
                arg2 = float(nums[1])
                arg3 = 1.
            elif len(nums) == 3:
                arg1 = float(nums[0])
                arg2 = float(nums[1])
                arg3 = float(nums[2])
            else:
                raise ValueError("Wrong range command.")
            return list(np.arange(arg1, arg2, arg3))
        else:
            raise ValueError("Wrong range command.")

    # empty command
    if cmd == "":
        return []

    # get number of ','
    n_comma = cmd.count(",")

    if n_comma > 0:
        # parse cmd given that it contains only ','
        return parse_float_range_command_with_comma(cmd)
    elif n_comma == 0 and (str_is_int(cmd) or str_is_float(cmd)):
        # cmd has the form of "10"
        return [float(cmd)]
    else:
        raise ValueError("Wrong command.")


def parse_slicing_command_with_comma(cmd, length):
    r"""
    Function that parses a command for slicing which contains at least one comma
    (``,``). The function returns a `list` with the integer values that are
    included in the command. It also ignores any redundant whitespaces that may
    exist in the command. For example ::

        parse_slicing_command_with_comma([1, 2,-3 ], 10)

    returns ::

        '[1, 2, -3]'

    Parameter
    ---------
    cmd : `str`
        The command string.
    length : `int`
        The length of the variable that will get sliced.

    Returns
    -------
    cmd_list : `list`
        The list that can be used for slicing after interpreting and evaluating
        the provided command.

    Raises
    ------
    ValueError
        Command cannot start or end with ','.
    ValueError
        Command cannot contain a pattern of the form ',,'.
    ValueError
        Command cannot contain numbers greater than {length}.
    ValueError
        Command must contain positive or negative integers.
    """
    if cmd.startswith(',') or cmd.endswith(','):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(',')
        # for each part
        final_cmd = []
        for i in tmp_cmd:
            if len(i) == 0:
                # this means that there was the ',,' pattern
                raise ValueError("Command cannot contain a pattern of the "
                                 "form ',,'.")
            elif str_is_int(i):
                # if it is a positive or negative integer convert it to int
                n = int(i)
                if n >= length:
                    raise ValueError("Command cannot contain numbers greater "
                                     "than {}.".format(length))
                else:
                    final_cmd.append(n)
            else:
                # else raise an error
                raise ValueError("Command must contain positive or negative "
                                 "integers.")
        return final_cmd


def parse_slicing_command_with_one_colon(cmd, length):
    r"""
    Function that parses a command for slicing which contains exactly one colon
    (``:``). The function returns a `list` with the integer indices, after
    interpreting the slicing command. It also ignores any redundant whitespaces
    that may exist in the command. For example ::

        parse_slicing_command_with_one_colon(:3, 10)

    returns ::

        '[0, 1, 2]'

    Parameters
    ----------
    cmd : `str`
        The command string.
    length : `int`
        The length of the variable that will get sliced.

    Returns
    -------
    cmd_list : `list`
        The list that can be used for slicing after interpreting and evaluating
        the provided command.

    Raises
    ------
    ValueError
        Command cannot contain numbers greater than {length}.
    ValueError
        Command must contain positive or negative integers.
    """
    # this is necessary in order to return ranges with negative slices
    tmp_list = range(length)

    if cmd.startswith(':'):
        # cmd has the form ":3" or ":"
        if len(cmd) > 1:
            # cmd has the form ":3"
            i = cmd[1:]
            if str_is_int(i):
                n = int(i)
                if n > length:
                    raise ValueError("Command cannot contain numbers greater "
                                     "than {}.".format(length))
                else:
                    return tmp_list[:n]
            else:
                raise ValueError("Command must contain integers.")
        else:
            # cmd is ":"
            return tmp_list
    elif cmd.endswith(':'):
        # cmd has the form "3:" or ":"
        if len(cmd) > 1:
            # cmd has the form "3:"
            i = cmd[:-1]
            if str_is_int(i):
                n = int(i)
                if n >= length:
                    raise ValueError("Command cannot contain numbers greater "
                                     "than {}.".format(length))
                else:
                    return tmp_list[n:]
            else:
                raise ValueError("Command must contain integers.")
        else:
            # cmd is ":"
            return tmp_list
    else:
        # cmd has the form "3:10"
        # get the parts before and after colon
        tmp_cmd = cmd.split(':')
        start = tmp_cmd[0]
        end = tmp_cmd[1]

        if str_is_int(start) and str_is_int(end):
            start = int(start)
            end = int(end)
            if start >= length or end > length:
                raise ValueError("Command cannot contain numbers greater "
                                 "than {}.".format(length))
            else:
                return tmp_list[start:end]
        else:
            raise ValueError("Command must contain integers.")


def parse_slicing_command_with_two_colon(cmd, length):
    r"""
    Function that parses a command for slicing which contains exactly two colons
    (``:``). The function returns a `list` with the integer indices, after
    interpreting the slicing command. It also ignores any redundant whitespaces
    that may exist in the command. For example ::

        parse_slicing_command_with_two_colon(::3, 10)

    returns ::

        '[0, 3, 6, 9]'

    Parameters
    ----------
    cmd : `str`
        The command string.
    length : `int`
        The length of the variable that will get sliced.

    Returns
    -------
    cmd_list : `list`
        The list that can be used for slicing after interpreting and evaluating
        the provided command.

    Raises
    ------
    ValueError
        Command cannot contain numbers greater than {length}.
    ValueError
        Command must contain positive or negative integers.
    """
    # this is necessary in order to return ranges with negative slices
    tmp_list = range(length)

    if cmd.startswith('::'):
        # cmd has the form "::3" or "::"
        if len(cmd) > 2:
            # cmd has the form "::3"
            i = cmd[2:]
            if str_is_int(i):
                n = int(i)
                return tmp_list[::n]
            else:
                raise ValueError("Command must contain integers.")
        else:
            # cmd is "::"
            return tmp_list
    elif cmd.endswith('::'):
        # cmd has the form "3::" or "::"
        if len(cmd) > 2:
            # cmd has the form "3::"
            i = cmd[:-2]
            if str_is_int(i):
                n = int(i)
                if n >= length:
                    raise ValueError("Command cannot contain numbers greater "
                                     "than {}.".format(length))
                else:
                    return tmp_list[n::]
            else:
                raise ValueError("Command must contain integers.")
        else:
            # cmd is "::"
            return tmp_list
    else:
        # cmd has the form "1:8:2"
        # get the parts in between colons
        tmp_cmd = cmd.split(':')

        start = tmp_cmd[0]
        end = tmp_cmd[1]
        step = tmp_cmd[2]

        if str_is_int(start) and str_is_int(end) and str_is_int(step):
            start = int(start)
            end = int(end)
            step = int(step)
            if start >= length or end > length:
                raise ValueError("Command cannot contain numbers greater "
                                 "than {}.".format(length))
            else:
                return tmp_list[start:end:step]
        else:
            raise ValueError("Command must contain integers.")


def parse_slicing_command(cmd, length):
    r"""
    Function that parses a command for slicing. It is able to recognize any
    slicing pattern of Python and detect pattern errors. Some characteristic
    examples are ":3", ":-2", "3:", "::3", "3::", "1:8", "1:8:2", "1, 5, -3",
    "range(10)", "range("1, 10, 2)" etc. The function returns a `list` with the
    integer indices, after interpreting the slicing command. It also ignores any
    redundant whitespaces that may exist in the command.

    Parameters
    ----------
    cmd : `str`
        The command string.
    length : `int`
        The length of the variable that will get sliced.

    Returns
    -------
    cmd_list : `list`
        The list that can be used for slicing after interpreting and evaluating
        the provided command.

    Raises
    ------
    ValueError
        Command cannot contain numbers greater than {length}.
    ValueError
        Command must contain positive or negative integers.
    """
    # remove all redundant spaces from cmd
    cmd = cmd.replace(" ", "")

    # remove all brackets from cmd
    cmd = cmd.replace("[", "")
    cmd = cmd.replace("]", "")

    # cmd has the form of "range(1, 10, 2)" or "range(10)"
    if cmd.startswith("range("):
        if cmd.endswith(")"):
            cmd = cmd[6:-1]
            if cmd.count(",") > 0:
                cmd = cmd.replace(",", ":")
            else:
                cmd = "0:" + cmd
        else:
            raise ValueError("Wrong command.")

    # empty command
    if cmd == "":
        return []

    # get number of ':' and number of ','
    n_colon = cmd.count(":")
    n_comma = cmd.count(",")

    if n_comma > 0 and n_colon == 0:
        # parse cmd given that it contains only ','
        return parse_slicing_command_with_comma(cmd, length)
    elif n_comma == 0 and n_colon > 0:
        # parse cmd given that it contains only ':'
        if n_colon == 1:
            return parse_slicing_command_with_one_colon(cmd, length)
        elif n_colon == 2:
            return parse_slicing_command_with_two_colon(cmd, length)
        else:
            raise ValueError("More than 2 ':'.")
    elif n_comma == 0 and n_colon == 0:
        # cmd has the form of "10"
        if str_is_int(cmd):
            n = int(cmd)
            if n >= length:
                raise ValueError("Cannot contain numbers greater "
                                 "than {}".format(length))
            else:
                return [n]
        else:
            raise ValueError("Wrong command.")
    else:
        raise ValueError("Wrong command.")


def list_has_constant_step(l):
    r"""
    Function that checks if a list of integers has a constant step between them
    and returns the step.

    Parameters
    ----------
    l : `list`
        The list to check.

    Returns
    -------
    has_constant_step : `bool`
        ``True`` if the `list` elements have a constant step between them.
    step : `int`
        The step value. ``None`` if `has_constant_step` is ``False``.
    """
    if len(l) <= 1:
        return False, None
    step = l[1] - l[0]
    s = step
    i = 2
    while s == step and i < len(l):
        s = l[i] - l[i - 1]
        i += 1
    if i == len(l) and s == step:
        return True, step
    else:
        return False, None
