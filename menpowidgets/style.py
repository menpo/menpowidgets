from io import BytesIO


def map_styles_to_hex_colours(style, background=False):
    r"""
    Function that returns the corresponding hex colour of a given style.

    Parameters
    ----------
    style : `str` or ``None`` (see below)
        Style options ::

            {``'success'``, ``'info'``, ``'warning'``, ``'danger'``, ``''``}
            or
            ``None``

    background : `bool`, optional
        If `True`, it returns the background (light) colour of each style.

    Returns
    -------
    hex_colour : `str`
        The corresponding hex colour.
    """
    if background:
        if style == "info":
            return "#D9EDF7"
        elif style == "danger":
            return "#F2DEDE"
        elif style == "success":
            return "#DFF0D8"
        elif style == "warning":
            return "#FCF8E3"
        elif style == "primary":
            return "#337ab7"
        else:
            return None
    else:
        if style == "info":
            return "#31708f"
        elif style == "danger":
            return "#A52A2A"
        elif style == "success":
            return "#228B22"
        elif style == "warning":
            return "#8A6D3B"
        elif style == "primary":
            return "#337ab7"
        else:
            return None


def parse_font_awesome_icon(option):
    r"""
    Function that parses an argument related to the `icon` and `description`
    properties of `ipywidgets.Button`. If the provided option is an `str` that
    starts with `fa-`, then a font-awesome icon is assumed.

    Parameters
    ----------
    option : `str` or ``None``
        The selected `description` option.

    Returns
    -------
    icon : `str` or ``None``
        The selected icon option.
    description : `str` or ``None``
        The selected description option.
    """
    if option is None:
        icon = description = None
    else:
        if len(option) > 3 and option[:3] == "fa-":
            icon = option
            description = ""
        else:
            icon = None
            description = option
    return icon, description


def convert_image_to_bytes(image):
    r"""
    Function that given a :map:`Image` object, it converts it to the correct
    bytes format that can be used by IPython.html.widgets.Image().
    """
    fp = BytesIO()
    image.as_PILImage().save(fp, format="png")
    fp.seek(0)
    return fp.read()
