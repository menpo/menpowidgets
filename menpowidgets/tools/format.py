try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


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
        if style == 'info':
            return '#D9EDF7'
        elif style == 'danger':
            return '#F2DEDE'
        elif style == 'success':
            return '#DFF0D8'
        elif style == 'warning':
            return '#FCF8E3'
        elif style == 'primary':
            return '#337ab7'
        else:
            return None
    else:
        if style == 'info':
            return '#31708f'
        elif style == 'danger':
            return '#A52A2A'
        elif style == 'success':
            return '#228B22'
        elif style == 'warning':
            return '#8A6D3B'
        elif style == 'primary':
            return '#337ab7'
        else:
            return None


def format_box(box, box_style, border_visible, border_color, border_style,
               border_width, border_radius, padding, margin):
    r"""
    Function that defines the style of an IPython box.

    Parameters
    ----------
    box : `IPython.html.widgets.Box`, `IPython.html.widgets.FlexBox` or subclass
        The ipython box object.
    box_style : `str` or ``None`` (see below)
        Style options ::

            {``'success'``, ``'info'``, ``'warning'``, ``'danger'``, ``''``}
            or
            ``None``

    border_visible : `bool`
        Defines whether to draw the border line around the widget.
    border_color : `str`
        The color of the border around the widget.
    border_style : `str`
        The line style of the border around the widget.
    border_width : `float`
        The line width of the border around the widget.
    border_radius : `float`
        The radius of the corners of the box.
    padding : `float`
        The padding around the widget.
    margin : `float`
        The margin around the widget.
    """
    box.box_style = box_style
    box.padding = padding
    box.margin = margin
    if border_visible:
        box.border_color = border_color
        box.border_style = border_style
        box.border_width = border_width
        box.border_radius = border_radius
    else:
        box.border_width = 0


def format_font(obj, font_family, font_size, font_style, font_weight):
    r"""
    Function that defines the font of a given IPython object.

    Parameters
    ----------
    obj : `IPython.html.widgets`
        The ipython widget object.
    font_family : See Below, optional
        The font of the axes.
        Example options ::

            {``serif``, ``sans-serif``, ``cursive``, ``fantasy``,
             ``monospace``}

    font_size : `int`, optional
        The font size of the axes.
    font_style : {``normal``, ``italic``, ``oblique``}, optional
        The font style of the axes.
    font_weight : See Below, optional
        The font weight of the axes.
        Example options ::

            {``ultralight``, ``light``, ``normal``, ``regular``,
             ``book``, ``medium``, ``roman``, ``semibold``,
             ``demibold``, ``demi``, ``bold``, ``heavy``,
             ``extra bold``, ``black``}
    """
    obj.font_family = font_family
    obj.font_size = font_size
    obj.font_style = font_style
    obj.font_weight = font_weight


def convert_image_to_bytes(image):
    r"""
    Function that given a :map:`Image` object, it converts it to the correct
    bytes format that can be used by IPython.html.widgets.Image().
    """
    fp = StringIO()
    image.as_PILImage().save(fp, format='png')
    fp.seek(0)
    return fp.read()
