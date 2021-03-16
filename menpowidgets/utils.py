from struct import pack as struct_pack
import binascii
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
    return "#" + binascii.hexlify(struct_pack("BBB", *rgb)).decode("ascii")


def decode_colour(colour):
    if not isinstance(colour, str):
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
    return s.isdigit() or (s.startswith("-") and s[1:].isdigit())


def str_is_float(s):
    r"""
    Function that returns ``True`` if a given `str` is a positive or negative
    float.

    Parameters
    ----------
    s : `str`
        The command string.
    """
    return s.count(".") == 1 and str_is_int(s.replace(".", "", 1))


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
    if cmd.startswith(",") or cmd.endswith(","):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(",")
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
            return eval("list({})".format(cmd))
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
    if cmd.startswith(",") or cmd.endswith(","):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(",")
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
            nums = cmd[6:-1].split(",")
            if len(nums) == 1:
                arg1 = 0.0
                arg2 = float(nums[0])
                arg3 = 1.0
            elif len(nums) == 2:
                arg1 = float(nums[0])
                arg2 = float(nums[1])
                arg3 = 1.0
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
    if cmd.startswith(",") or cmd.endswith(","):
        # if cmd starts or ends with ',', raise an error
        raise ValueError("Command cannot start or end with ','.")
    else:
        # get the parts in between commas
        tmp_cmd = cmd.split(",")
        # for each part
        final_cmd = []
        for i in tmp_cmd:
            if len(i) == 0:
                # this means that there was the ',,' pattern
                raise ValueError(
                    "Command cannot contain a pattern of the " "form ',,'."
                )
            elif str_is_int(i):
                # if it is a positive or negative integer convert it to int
                n = int(i)
                if n >= length:
                    raise ValueError(
                        "Command cannot contain numbers greater "
                        "than {}.".format(length)
                    )
                else:
                    final_cmd.append(n)
            else:
                # else raise an error
                raise ValueError(
                    "Command must contain positive or negative " "integers."
                )
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
    tmp_list = list(range(length))

    if cmd.startswith(":"):
        # cmd has the form ":3" or ":"
        if len(cmd) > 1:
            # cmd has the form ":3"
            i = cmd[1:]
            if str_is_int(i):
                n = int(i)
                if n > length:
                    raise ValueError(
                        "Command cannot contain numbers greater "
                        "than {}.".format(length)
                    )
                else:
                    return tmp_list[:n]
            else:
                raise ValueError("Command must contain integers.")
        else:
            # cmd is ":"
            return tmp_list
    elif cmd.endswith(":"):
        # cmd has the form "3:" or ":"
        if len(cmd) > 1:
            # cmd has the form "3:"
            i = cmd[:-1]
            if str_is_int(i):
                n = int(i)
                if n >= length:
                    raise ValueError(
                        "Command cannot contain numbers greater "
                        "than {}.".format(length)
                    )
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
        tmp_cmd = cmd.split(":")
        start = tmp_cmd[0]
        end = tmp_cmd[1]

        if str_is_int(start) and str_is_int(end):
            start = int(start)
            end = int(end)
            if start >= length or end > length:
                raise ValueError(
                    "Command cannot contain numbers greater " "than {}.".format(length)
                )
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
    tmp_list = list(range(length))

    if cmd.startswith("::"):
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
    elif cmd.endswith("::"):
        # cmd has the form "3::" or "::"
        if len(cmd) > 2:
            # cmd has the form "3::"
            i = cmd[:-2]
            if str_is_int(i):
                n = int(i)
                if n >= length:
                    raise ValueError(
                        "Command cannot contain numbers greater "
                        "than {}.".format(length)
                    )
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
        tmp_cmd = cmd.split(":")

        start = tmp_cmd[0]
        end = tmp_cmd[1]
        step = tmp_cmd[2]

        if str_is_int(start) and str_is_int(end) and str_is_int(step):
            start = int(start)
            end = int(end)
            step = int(step)
            if start >= length or end > length:
                raise ValueError(
                    "Command cannot contain numbers greater " "than {}.".format(length)
                )
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
                raise ValueError(
                    "Cannot contain numbers greater " "than {}".format(length)
                )
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
        return False, 1
    step = l[1] - l[0]
    s = step
    i = 2
    while s == step and i < len(l):
        s = l[i] - l[i - 1]
        i += 1
    if i == len(l) and s == step:
        return True, step
    else:
        return False, 1


def sample_colours_from_colourmap(n_colours, colour_map):
    import matplotlib.pyplot as plt

    cm = plt.get_cmap(colour_map)
    colours = []
    for i in range(n_colours):
        c = cm(1.0 * i / n_colours)[:3]
        colours.append(decode_colour([int(i * 255) for i in c]))
    return colours


def extract_group_labels_from_landmarks(landmark_manager):
    groups_keys = None
    labels_keys = None
    if landmark_manager.has_landmarks:
        groups_keys = landmark_manager.group_labels
        labels_keys = []
        for g in groups_keys:
            if hasattr(landmark_manager[g], "labels"):
                labels_keys.append(landmark_manager[g].labels)
            else:
                labels_keys.append(None)
    return groups_keys, labels_keys


def extract_groups_labels_from_image(image):
    r"""
    Function that extracts the groups and labels from an image's landmarks.

    Parameters
    ----------
    image : :map:`Image` or subclass
       The input image object.

    Returns
    -------
    group_keys : `list` of `str`
        The list of landmark groups found.

    labels_keys : `list` of `str`
        The list of lists of each landmark group's labels.
    """
    groups_keys, labels_keys = extract_group_labels_from_landmarks(image.landmarks)
    return groups_keys, labels_keys


def render_image(
    image,
    renderer,
    render_landmarks,
    image_is_masked,
    masked_enabled,
    channels,
    group,
    with_labels,
    render_lines,
    line_style,
    line_width,
    line_colour,
    render_markers,
    marker_style,
    marker_size,
    marker_edge_width,
    marker_edge_colour,
    marker_face_colour,
    render_numbering,
    numbers_font_name,
    numbers_font_size,
    numbers_font_style,
    numbers_font_weight,
    numbers_font_colour,
    numbers_horizontal_align,
    numbers_vertical_align,
    legend_n_columns,
    legend_border_axes_pad,
    legend_rounded_corners,
    legend_title,
    legend_horizontal_spacing,
    legend_shadow,
    legend_location,
    legend_font_name,
    legend_bbox_to_anchor,
    legend_border,
    legend_marker_scale,
    legend_vertical_spacing,
    legend_font_weight,
    legend_font_size,
    render_legend,
    legend_font_style,
    legend_border_padding,
    figure_size,
    render_axes,
    axes_font_name,
    axes_font_size,
    axes_font_style,
    axes_font_weight,
    axes_x_limits,
    axes_y_limits,
    axes_x_ticks,
    axes_y_ticks,
    interpolation,
    alpha,
    cmap_name,
):
    # This makes the code shorter for dealing with masked images vs non-masked
    # images
    mask_arguments = {"masked": masked_enabled} if image_is_masked else {}

    # plot
    if render_landmarks and group is not None:
        renderer = image.view_landmarks(
            channels=channels,
            group=group,
            with_labels=with_labels,
            without_labels=None,
            figure_id=renderer.figure_id,
            new_figure=False,
            render_lines=render_lines,
            line_colour=line_colour,
            line_style=line_style,
            line_width=line_width,
            render_markers=render_markers,
            marker_style=marker_style,
            marker_size=marker_size,
            marker_face_colour=marker_face_colour,
            marker_edge_colour=marker_edge_colour,
            marker_edge_width=marker_edge_width,
            render_numbering=render_numbering,
            numbers_horizontal_align=numbers_horizontal_align,
            numbers_vertical_align=numbers_vertical_align,
            numbers_font_name=numbers_font_name,
            numbers_font_size=numbers_font_size,
            numbers_font_style=numbers_font_style,
            numbers_font_weight=numbers_font_weight,
            numbers_font_colour=numbers_font_colour,
            render_legend=render_legend,
            legend_title=legend_title,
            legend_font_name=legend_font_name,
            legend_font_style=legend_font_style,
            legend_font_size=legend_font_size,
            legend_font_weight=legend_font_weight,
            legend_marker_scale=legend_marker_scale,
            legend_location=legend_location,
            legend_bbox_to_anchor=legend_bbox_to_anchor,
            legend_border_axes_pad=legend_border_axes_pad,
            legend_n_columns=legend_n_columns,
            legend_horizontal_spacing=legend_horizontal_spacing,
            legend_vertical_spacing=legend_vertical_spacing,
            legend_border=legend_border,
            legend_border_padding=legend_border_padding,
            legend_shadow=legend_shadow,
            legend_rounded_corners=legend_rounded_corners,
            render_axes=render_axes,
            axes_font_name=axes_font_name,
            axes_font_size=axes_font_size,
            axes_font_style=axes_font_style,
            axes_font_weight=axes_font_weight,
            axes_x_limits=axes_x_limits,
            axes_y_limits=axes_y_limits,
            axes_x_ticks=axes_x_ticks,
            axes_y_ticks=axes_y_ticks,
            figure_size=figure_size,
            interpolation=interpolation,
            alpha=alpha,
            cmap_name=cmap_name,
            **mask_arguments
        )
    else:
        # either there are not any landmark groups selected or they won't
        # be displayed
        renderer = image.view(
            channels=channels,
            render_axes=render_axes,
            axes_font_name=axes_font_name,
            axes_font_size=axes_font_size,
            axes_font_style=axes_font_style,
            axes_font_weight=axes_font_weight,
            axes_x_limits=axes_x_limits,
            axes_y_limits=axes_y_limits,
            figure_size=figure_size,
            interpolation=interpolation,
            alpha=alpha,
            cmap_name=cmap_name,
            **mask_arguments
        )

    # show plot
    renderer.force_draw()

    return renderer


def render_patches(
    patches,
    patch_centers,
    patches_indices,
    offset_index,
    renderer,
    background,
    render_patches,
    channels,
    interpolation,
    cmap_name,
    alpha,
    render_patches_bboxes,
    bboxes_line_colour,
    bboxes_line_style,
    bboxes_line_width,
    render_centers,
    render_lines,
    line_colour,
    line_style,
    line_width,
    render_markers,
    marker_style,
    marker_size,
    marker_face_colour,
    marker_edge_colour,
    marker_edge_width,
    render_numbering,
    numbers_horizontal_align,
    numbers_vertical_align,
    numbers_font_name,
    numbers_font_size,
    numbers_font_style,
    numbers_font_weight,
    numbers_font_colour,
    render_axes,
    axes_font_name,
    axes_font_size,
    axes_font_style,
    axes_font_weight,
    axes_x_limits,
    axes_y_limits,
    axes_x_ticks,
    axes_y_ticks,
    figure_size,
):
    from menpo.transform import UniformScale
    from menpo.visualize import view_patches

    renderer = view_patches(
        patches,
        patch_centers,
        patches_indices=patches_indices,
        offset_index=offset_index,
        figure_id=renderer.figure_id,
        new_figure=False,
        background=background,
        render_patches=render_patches,
        channels=channels,
        interpolation=interpolation,
        cmap_name=cmap_name,
        alpha=alpha,
        render_patches_bboxes=render_patches_bboxes,
        bboxes_line_colour=bboxes_line_colour,
        bboxes_line_style=bboxes_line_style,
        bboxes_line_width=bboxes_line_width,
        render_centers=render_centers,
        render_lines=render_lines,
        line_colour=line_colour,
        line_style=line_style,
        line_width=line_width,
        render_markers=render_markers,
        marker_style=marker_style,
        marker_size=marker_size,
        marker_face_colour=marker_face_colour,
        marker_edge_colour=marker_edge_colour,
        marker_edge_width=marker_edge_width,
        render_numbering=render_numbering,
        numbers_horizontal_align=numbers_horizontal_align,
        numbers_vertical_align=numbers_vertical_align,
        numbers_font_name=numbers_font_name,
        numbers_font_size=numbers_font_size,
        numbers_font_style=numbers_font_style,
        numbers_font_weight=numbers_font_weight,
        numbers_font_colour=numbers_font_colour,
        render_axes=render_axes,
        axes_font_name=axes_font_name,
        axes_font_size=axes_font_size,
        axes_font_style=axes_font_style,
        axes_font_weight=axes_font_weight,
        axes_x_limits=axes_x_limits,
        axes_y_limits=axes_y_limits,
        axes_x_ticks=axes_x_ticks,
        axes_y_ticks=axes_y_ticks,
        figure_size=figure_size,
    )

    # show plot
    renderer.force_draw()

    return renderer
