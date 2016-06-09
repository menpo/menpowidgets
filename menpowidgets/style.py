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


def format_box(box, box_style='', border_visible=False, border_colour='black',
               border_style='solid', border_width=1, border_radius=0,
               padding=0, margin=0):
    r"""
    Function that defines the style of an `ipywidgets.Box`, `ipywidgets.FlexBox`
    or subclass object.

    Parameters
    ----------
    box : `ipywidgets.Box`, `ipywidgets.FlexBox` or subclass
        The box object.
    box_style : `str` or ``None`` (see below)
        Style options ::

            {``'success'``, ``'info'``, ``'warning'``, ``'danger'``, ``''``}
            or
            ``None``

    border_visible : `bool`
        Defines whether to draw the border line around the widget.
    border_colour : `str`
        The colour of the border around the widget.
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
        box.border_color = border_colour
        box.border_style = border_style
        box.border_width = border_width
        box.border_radius = border_radius
    else:
        box.border_width = 0


def format_font(obj, font_family='', font_size=None, font_style='',
                font_weight=''):
    r"""
    Function that defines the font of a given `ipywidgets` object.

    Parameters
    ----------
    obj : `ipywidgets`
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


def format_slider(obj, slider_width='6cm', slider_handle_colour=None,
                  slider_bar_colour=None, slider_text_visible=True):
    r"""
    Function that defines the options of a given `ipywidgets` slider object.

    Parameters
    ----------
    obj : `ipywidgets.IntSlider` or `ipywidgets.FloatSlider`
        The ipython slider object.
    slider_width : float, optional
        The width of the slider.
    slider_handle_colour : `str`, optional
        The colour of the slider's handle.
    slider_bar_colour : `str`, optional
        The colour of the slider's bar.
    slider_text_visible : `bool`, optional
        Whether the slider's text is visible.
    """
    obj.width = slider_width
    obj.slider_color = slider_handle_colour
    obj.background_color = slider_bar_colour
    obj.readout = slider_text_visible


def format_text_box(obj, colour=None, background_colour=None):
    r"""
    Function that defines the options of a given `ipywidgets` text box object,
    such as `Text`, `TextArea`, `IntText`, `Select` etc.

    Parameters
    ----------
    obj : `ipywidgets` textbox-like object
        The ipython object.
    colour : `str`, optional
        The text colour of the widget.
    background_colour : `str`, optional
        The background colour of the widget.
    """
    obj.background_color = background_colour
    obj.color = colour


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
        if len(option) > 3 and option[:3] == 'fa-':
            icon = option
            description = ''
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
    image.as_PILImage().save(fp, format='png')
    fp.seek(0)
    return fp.read()
