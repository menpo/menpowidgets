from collections import OrderedDict
import ipywidgets
from traitlets import link
from traitlets.traitlets import List

import menpo.io as mio

from .style import (map_styles_to_hex_colours, convert_image_to_bytes,
                    format_box, format_font, format_slider, format_text_box,
                    parse_font_awesome_icon)
from .utils import (lists_are_the_same, decode_colour, parse_slicing_command,
                    list_has_constant_step, parse_int_range_command,
                    parse_float_range_command)

# Global variables to try and reduce overhead of loading the logo
MENPO_MINIMAL_LOGO = None
MENPO_DANGER_LOGO = None
MENPO_WARNING_LOGO = None
MENPO_SUCCESS_LOGO = None
MENPO_INFO_LOGO = None
MENPO_LOGO_SCALE = None


class MenpoWidget(ipywidgets.FlexBox):
    def __init__(self, children, trait, trait_default_value,
                 render_function=None, orientation='vertical', align='start'):
        # Create box object
        super(MenpoWidget, self).__init__(children=children)
        self.orientation = orientation
        self.align = align

        # Add trait for selected values
        selected_values = trait(default_value=trait_default_value)
        selected_values_trait = {'selected_values': selected_values}
        self.add_traits(**selected_values_trait)

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.on_trait_change(self._render_function, 'selected_values')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.on_trait_change(self._render_function, 'selected_values',
                             remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)


class LogoWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget with Menpo's logo image. The widget stores the image in
    `self.image` using `ipywidgets.Image`.

    To set the styling of this widget please refer to the `style()` method.

    Parameters
    ----------
    scale : `float`, optional
        Defines the scale that will be applied to the logo image
        (`logos/menpo_thumbnail.jpg`).
    style : ``{'minimal', 'danger', 'info', 'warning', 'success'}``, optional
        Defines the styling of the logo widget, i.e. the colour around the
        logo image.
    """
    def __init__(self, scale=0.3, style='minimal'):
        from menpowidgets.base import menpowidgets_src_dir_path
        # Try to only load the logo once
        global MENPO_LOGO_SCALE
        logos_path = menpowidgets_src_dir_path() / 'logos'
        if style == 'minimal':
            global MENPO_MINIMAL_LOGO
            if MENPO_MINIMAL_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_MINIMAL_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_MINIMAL_LOGO))
        elif style == 'danger':
            global MENPO_DANGER_LOGO
            if MENPO_DANGER_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_DANGER_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_DANGER_LOGO))
        elif style == 'info':
            global MENPO_INFO_LOGO
            if MENPO_INFO_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_INFO_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_INFO_LOGO))
        elif style == 'warning':
            global MENPO_WARNING_LOGO
            if MENPO_WARNING_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_WARNING_LOGO = image.rescale(scale)
                MENPO_LOGO_SCALE = scale
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_WARNING_LOGO))
        elif style == 'success':
            global MENPO_SUCCESS_LOGO
            if MENPO_SUCCESS_LOGO is None or scale != MENPO_LOGO_SCALE:
                image = mio.import_image(logos_path / "menpo_{}.jpg".format(
                    style))
                MENPO_SUCCESS_LOGO = image.rescale(scale)
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_SUCCESS_LOGO))
        else:
            raise ValueError("style must be 'minimal', 'info', 'danger', "
                             "'warning' or 'success'; {} was "
                             "given.".format(style))
        super(LogoWidget, self).__init__(children=[self.image])

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0):
        r"""
        Function that defines the style of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)


class ListWidget(MenpoWidget):
    r"""
    Creates a widget for selecting a list with numbers. It supports both
    integers and floats.

    The selected values are stored in the `self.selected_values` `trait`. To
    set the styling of this widget please refer to the `style()` method. To
    update the state and function of the widget, please refer to the
    `set_widget_state()` and `replace_render_function()` methods.

    Parameters
    ----------
    selected_list : `list`
        The initial list.
    mode : ``{'int', 'float'}``, optional
        Defines the data type of the list members.
    description : `str`, optional
        The description of the command text box.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If `True`, then a line with command examples is printed below the
        main text box.
    """
    def __init__(self, selected_list, mode='float', description='Command:',
                 render_function=None, example_visible=True):
        # Create command text widget
        selected_cmd = ''
        if mode == 'int':
            for i in selected_list:
                selected_cmd += '{}, '.format(i)
        elif mode == 'float':
            for i in selected_list:
                selected_cmd += '{:.1f}, '.format(i)
        else:
            raise ValueError("mode must be either int or float.")
        self.cmd_text = ipywidgets.Text(value=selected_cmd[:-2],
                                        description=description)

        # Create the rest of the widgets
        if mode == 'int':
            self.example = ipywidgets.Latex(
                value="e.g. '[1, 2]', '10', '10, 20', 'range(10)', "
                      "'range(1, 8, 2)' etc.",
                font_size=11, font_style='italic', visible=example_visible)
        else:
            self.example = ipywidgets.Latex(
                value="e.g. '10.', '10., 20.', 'range(10.)', "
                      "'range(2.5, 5., 2.)' etc.",
                font_size=11, font_style='italic', visible=example_visible)
        self.error_msg = ipywidgets.Latex(value='', font_style='italic',
                                          color='#FF0000')

        # Create final widget
        children = [self.cmd_text, self.example, self.error_msg]
        trait = List
        trait_default_value = selected_list
        super(ListWidget, self).__init__(
            children, trait, trait_default_value,
            render_function=render_function, orientation='vertical',
            align='end')

        # Assign properties
        self.mode = mode

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ''
            try:
                if self.mode == 'int':
                    self.selected_values = parse_int_range_command(
                        str(self.cmd_text.value))
                else:
                    self.selected_values = parse_float_range_command(
                        str(self.cmd_text.value))
            except ValueError as e:
                self.error_msg.value = str(e)
        self.cmd_text.on_submit(save_cmd)

    def set_widget_state(self, selected_list, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        selected_list : `list`
            The selected list.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if not lists_are_the_same(selected_list, self.selected_values):
            # Assign new options dict to selected_values
            selected_cmd = ''
            if self.mode == 'int':
                for i in selected_list:
                    selected_cmd += '{}, '.format(i)
            elif self.mode == 'float':
                for i in selected_list:
                    selected_cmd += '{:.1f}, '.format(i)

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update command text
            self.selected_values = selected_list
            self.cmd_text.value = selected_cmd[:-2]

            # re-assign render callback
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', 0)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, text_box_style=None, text_box_background_colour=None,
              text_box_width=None, font_family='', font_size=None,
              font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        text_box_style : `str` or ``None`` (see below), optional
            Command text box style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        text_box_background_colour : `str`, optional
            The background colour of the command text box.
        text_box_width : `str`, optional
            The width of the command text box.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.cmd_text, font_family, font_size, font_style,
                    font_weight)
        self.cmd_text.color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.background_color = map_styles_to_hex_colours(
            text_box_background_colour, background=True)
        self.cmd_text.border_color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.font_family = 'monospace'
        self.cmd_text.border_width = 1
        self.cmd_text.width = text_box_width


class SlicingCommandWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting a slicing command.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    slice_cmd : `dict`
        The initial slicing options. Example ::

            slice_cmd = {'indices': [0, 1, 2], 'command': ':3', 'length': 68}

    description : `str`, optional
        The description of the command text box.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If ``True``, then a line with command examples is printed below the
        main text box.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the slider's handle. If ``False``, then the the functions are
        called only when the handle (mouse click) is realised.
    """
    def __init__(self, slice_cmd, description='Command:',
                 render_function=None, example_visible=True,
                 continuous_update=False):
        # Create command text widget
        slice_cmd['indices'] = parse_slicing_command(slice_cmd['command'],
                                                     slice_cmd['length'])
        self.cmd_text = ipywidgets.Text(value=slice_cmd['command'],
                                        description=description)

        # Assign output
        self.selected_values = slice_cmd

        # Create the rest of the widgets
        self.example = ipywidgets.Latex(
            value="e.g. ':3', '-3:', '1:{}:2', '3::', '0, {}', '7', "
                  "'range({})' etc.".format(slice_cmd['length'],
                                            slice_cmd['length'],
                                            slice_cmd['length']),
            font_size=11, font_style='italic', visible=example_visible)
        self.error_msg = ipywidgets.Latex(value='', font_style='italic',
                                          color='#FF0000')
        self.single_slider = ipywidgets.IntSlider(
            min=0, max=slice_cmd['length']-1, value=0, width='6.8cm',
            visible=self._single_slider_visible(),
            continuous_update=continuous_update)
        self.multiple_slider = ipywidgets.IntRangeSlider(
            min=0, max=slice_cmd['length']-1,
            value=(slice_cmd['indices'][0], slice_cmd['indices'][-1]),
            width='6.8cm', visible=self._multiple_slider_visible()[0],
            continuous_update=continuous_update)
        super(SlicingCommandWidget, self).__init__(
            children=[self.cmd_text, self.example, self.error_msg,
                      self.single_slider, self.multiple_slider])
        self.orientation = 'vertical'
        self.align = 'end'

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ''
            try:
                self.selected_values['command'] = str(self.cmd_text.value)
                self.selected_values['indices'] = parse_slicing_command(
                    str(self.cmd_text.value), self.selected_values['length'])
            except ValueError as e:
                self.error_msg.value = str(e)

            # set single slider visibility and value
            self.single_slider.visible = self._single_slider_visible()
            if self._single_slider_visible():
                self.single_slider.on_trait_change(self._render_function,
                                                   'value', remove=True)
                self.single_slider.value = self.selected_values['indices'][0]
                self.single_slider.on_trait_change(self._render_function,
                                                   'value')

            # set multiple slider visibility and value
            vis, step = self._multiple_slider_visible()
            self.multiple_slider.visible = vis
            if vis:
                self.multiple_slider.step = step
                self.multiple_slider.on_trait_change(self._render_function,
                                                     'value', remove=True)
                self.multiple_slider.value = (
                    self.selected_values['indices'][0],
                    self.selected_values['indices'][-1])
                self.multiple_slider.on_trait_change(self._render_function,
                                                     'value')
        self.cmd_text.on_submit(save_cmd)

        def single_slider_value(name, value):
            self.selected_values['indices'] = [value]
            self.cmd_text.value = str(value)
            self.selected_values['command'] = str(value)
        self.single_slider.on_trait_change(single_slider_value, 'value')

        def multiple_slider_value(name, value):
            self.selected_values['indices'] = range(value[0], value[1]+1,
                                                    self.multiple_slider.step)
            self.cmd_text.value = "{}:{}:{}".format(value[0], value[1]+1,
                                                    self.multiple_slider.step)
            self.selected_values['command'] = str(self.cmd_text.value)
        self.multiple_slider.on_trait_change(multiple_slider_value, 'value')

        # Set render function
        self._render_function = None
        self._render_function_2 = None
        self.add_render_function(render_function)

    def _single_slider_visible(self):
        return len(self.selected_values['indices']) == 1

    def _multiple_slider_visible(self):
        return list_has_constant_step(self.selected_values['indices'])

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            def render_function_2(name):
                self._render_function(name, '')

            self._render_function_2 = render_function_2

            self.cmd_text.on_submit(self._render_function_2)
            self.single_slider.on_trait_change(self._render_function, 'value')
            self.multiple_slider.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.cmd_text.on_submit(self._render_function_2, remove=True)
        self.single_slider.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self.multiple_slider.on_trait_change(self._render_function, 'value',
                                             remove=True)
        self._render_function = None
        self._render_function_2 = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, slice_cmd, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        slice_cmd : `dict`
            The initial slicing options. Example ::

                slice_cmd = {'indices': [10], 'command': '10', 'length': 30}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        slice_cmd['indices'] = parse_slicing_command(slice_cmd['command'],
                                                     slice_cmd['length'])
        self.selected_values = slice_cmd

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update single slider
        self.single_slider.visible = self._single_slider_visible()
        self.single_slider.max = self.selected_values['length'] - 1
        if self._single_slider_visible():
            self.single_slider.value = self.selected_values['indices'][0]

        # update multiple slider
        vis, step = self._multiple_slider_visible()
        self.multiple_slider.visible = vis
        self.multiple_slider.max = slice_cmd['length'] - 1
        if vis:
            self.multiple_slider.step = step
            self.multiple_slider.value = (slice_cmd['indices'][0],
                                          slice_cmd['indices'][-1])

        # update command text
        self.cmd_text.value = self.selected_values['command']

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', 0)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, text_box_style=None, text_box_background_colour=None,
              text_box_width=None, font_family='', font_size=None,
              font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        text_box_style : `str` or ``None`` (see below), optional
            Command text box style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        text_box_background_colour : `str`, optional
            The background colour of the command text box.
        text_box_width : `str`, optional
            The width of the command text box.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.cmd_text, font_family, font_size, font_style,
                    font_weight)
        self.cmd_text.color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.background_color = map_styles_to_hex_colours(
            text_box_background_colour, background=True)
        self.cmd_text.border_color = map_styles_to_hex_colours(text_box_style)
        self.cmd_text.font_family = 'monospace'
        self.cmd_text.border_width = 1
        self.cmd_text.width = text_box_width
        self.single_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.single_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.multiple_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.multiple_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)


class IndexSliderWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting an index using a slider.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `set_render_function()` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the default options. For example ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    description : `str`, optional
        The title of the widget.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while moving
        the slider's handle. If ``False``, then the the functions are called only
        when the handle (mouse click) is realised.
    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    update_function : `function` or ``None``, optional
        The update function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, index, description='Index: ', continuous_update=False,
                 render_function=None, update_function=None):
        self.slider = ipywidgets.IntSlider(
            min=index['min'], max=index['max'], value=index['index'],
            step=index['step'], description=description, width='5cm',
            continuous_update=continuous_update)
        super(IndexSliderWidget, self).__init__(children=[self.slider])
        self.align = 'start'

        # Assign output
        self.selected_values = index

        # Set functionality
        def save_index(name, value):
            self.selected_values['index'] = value
        self.slider.on_trait_change(save_index, 'value')

        # Set render and update functions
        self._update_function = None
        self.add_update_function(update_function)
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='6cm', slider_bar_colour=None,
              slider_handle_colour=None, slider_text_visible=True):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        slider_width : `float`, optional
            The width of the slider
        slider_bar_colour : `str`, optional
            The colour of the slider's bar.
        slider_handle_colour : `str`, optional
            The colour of the slider's handle.
        slider_text_visible : `bool`, optional
            Whether the selected value of the slider is visible.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style,
                    font_weight)
        format_slider(self.slider, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=slider_text_visible)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.slider.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.slider.on_trait_change(self._render_function, 'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def add_update_function(self, update_function):
        r"""
        Method that adds a `update_function()` to the widget. The signature of
        the given function is also stored in `self._update_function`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._update_function = update_function
        if self._update_function is not None:
            self.slider.on_trait_change(self._update_function, 'value')

    def remove_update_function(self):
        r"""
        Method that removes the current `self._update_function()` from the
        widget and sets ``self._update_function = None``.
        """
        self.slider.on_trait_change(self._update_function, 'value', remove=True)
        self._update_function = None

    def replace_update_function(self, update_function):
        r"""
        Method that replaces the current `self._update_function()` of the widget
        with the given `update_function()`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_update_function()

        # add new function
        self.add_update_function(update_function)

    def set_widget_state(self, index, continuous_update=False,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        index : `dict`
            The dictionary with the selected options. For example ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        continuous_update : `bool`, optional
            If ``True``, then the render and update functions are called while
            moving the slider's handle. If ``False``, then the the functions are
            called only when the handle (mouse click) is realised.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (index != self.selected_values or
                self.slider.continuous_update != continuous_update):
            if not allow_callback:
                # temporarily remove render and update functions
                render_function = self._render_function
                update_function = self._update_function
                self.remove_render_function()
                self.remove_update_function()

            # set values to slider
            self.slider.continuous_update = continuous_update
            self.slider.min = index['min']
            self.slider.max = index['max']
            self.slider.step = index['step']
            self.slider.value = index['index']

            if not allow_callback:
                # re-assign render and update callbacks
                self.add_update_function(update_function)
                self.add_render_function(render_function)

        # Assign output
        self.selected_values = index


class IndexButtonsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting an index using plus/minus buttons.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the default options. For example ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    update_function : `function` or ``None``, optional
        The update function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that decreases the index. If the `str` starts
        with `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that increases the index. If the `str` starts
        with `'fa-'`, then a font-awesome icon is defined.
    loop_enabled : `bool`, optional
        If ``True``, then if by pressing the buttons we reach the minimum
        (maximum) index values, then the counting will continue from the end
        (beginning). If ``False``, the counting will stop at the minimum
        (maximum) value.
    text_editable : `bool`, optional
        Flag that determines whether the index text will be editable.
    """
    def __init__(self, index, render_function=None, update_function=None,
                 description='Index: ', minus_description='fa-minus',
                 plus_description='fa-plus', loop_enabled=True,
                 text_editable=True):
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(description=m_description,
                                              icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(description=p_description,
                                             icon=p_icon, width='1cm')
        self.index_text = ipywidgets.IntText(
            value=index['index'], min=index['min'], max=index['max'],
            disabled=not text_editable)
        super(IndexButtonsWidget, self).__init__(
            children=[self.title, self.button_minus, self.index_text,
                      self.button_plus])
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable

        # Style
        self.orientation = 'horizontal'
        self.align = 'start'

        # Assign output
        self.selected_values = index

        # Set functionality
        def value_plus(name):
            tmp_val = int(self.index_text.value) + self.selected_values['step']
            if tmp_val > self.selected_values['max']:
                if self.loop_enabled:
                    self.index_text.value = str(self.selected_values['min'])
                else:
                    self.index_text.value = str(self.selected_values['max'])
            else:
                self.index_text.value = str(tmp_val)
        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = int(self.index_text.value) - self.selected_values['step']
            if tmp_val < self.selected_values['min']:
                if self.loop_enabled:
                    self.index_text.value = str(self.selected_values['max'])
                else:
                    self.index_text.value = str(self.selected_values['min'])
            else:
                self.index_text.value = str(tmp_val)
        self.button_minus.on_click(value_minus)

        def save_index(name, value):
            self.selected_values['index'] = int(value)
        self.index_text.on_trait_change(save_index, 'value')

        # Set render and update functions
        self._update_function = None
        self.add_update_function(update_function)
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', minus_style='', plus_style='',
              text_colour=None, text_background_colour=None):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        minus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        plus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        text_colour : `str`, optional
            The text colour of the index text.
        text_background_colour : `str`, optional
            The background colour of the index text.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.index_text, font_family, font_size, font_style,
                    font_weight)
        self.button_minus.button_style = minus_style
        self.button_plus.button_style = plus_style
        format_text_box(self.index_text, text_colour, text_background_colour)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.index_text.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.index_text.on_trait_change(self._render_function, 'value',
                                        remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def add_update_function(self, update_function):
        r"""
        Method that adds a `update_function()` to the widget. The signature of
        the given function is also stored in `self._update_function`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._update_function = update_function
        if self._update_function is not None:
            self.index_text.on_trait_change(self._update_function, 'value')

    def remove_update_function(self):
        r"""
        Method that removes the current `self._update_function()` from the
        widget and sets ``self._update_function = None``.
        """
        self.index_text.on_trait_change(self._update_function, 'value',
                                        remove=True)
        self._update_function = None

    def replace_update_function(self, update_function):
        r"""
        Method that replaces the current `self._update_function()` of the widget
        with the given `update_function()`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_update_function()

        # add new function
        self.add_update_function(update_function)

    def set_widget_state(self, index, loop_enabled, text_editable,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        index : `dict`
            The dictionary with the selected options. For example ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        loop_enabled : `bool`, optional
            If ``True``, then if by pressing the buttons we reach the minimum
            (maximum) index values, then the counting will continue from the end
            (beginning). If ``False``, the counting will stop at the minimum
            (maximum) value.
        text_editable : `bool`, optional
            Flag that determines whether the index text will be editable.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Update loop_enabled and text_editable
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable
        self.index_text.disabled = not text_editable

        # Check if update is required
        if index != self.selected_values:
            if not allow_callback:
                # temporarily remove render and update functions
                render_function = self._render_function
                update_function = self._update_function
                self.remove_render_function()
                self.remove_update_function()

            # set value to index text
            self.index_text.min = index['min']
            self.index_text.max = index['max']
            self.index_text.value = str(index['index'])

            if not allow_callback:
                # re-assign render and update callbacks
                self.add_update_function(update_function)
                self.add_render_function(render_function)

        # Assign output
        self.selected_values = index


class ColourSelectionWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for colour selection of a single or multiple objects.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    colours_list : `list` of `str` or [`float`, `float`, `float`]
        If `str`, it must either a hex code or a colour name, such as ::

            {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
             'black', 'white'}

        If [`float`, `float`, `float`], it defines an RGB value and must have
        length 3.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The description of the widget.
    labels : `list` or ``None``, optional
        A `list` with the labels' names. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined.
    """
    def __init__(self, colours_list, render_function=None, description='Colour',
                 labels=None):
        # Check if multiple mode should be enabled
        if isinstance(colours_list, str) or isinstance(colours_list, unicode):
            colours_list = [colours_list]
        n_labels = len(colours_list)
        multiple = n_labels > 1
        self.description = description

        # Labels box (it must be invisible if multiple == False)
        labels_dict = OrderedDict()
        if labels is None:
            labels = []
            for k in range(n_labels):
                labels_dict["label {}".format(k)] = k
                labels.append("label {}".format(k))
        else:
            for k, l in enumerate(labels):
                labels_dict[l] = k
        self.label_dropdown = ipywidgets.Dropdown(description=description,
                                                  options=labels_dict, value=0)
        self.apply_to_all_button = ipywidgets.Button(
            description=' Apply to all', icon='fa-paint-brush')
        self.labels_box = ipywidgets.VBox(
            children=[self.label_dropdown, self.apply_to_all_button],
            visible=multiple, align='end')

        # Decode the colour of the first label
        default_colour = decode_colour(colours_list[0])

        # Create colour widget
        colour_description = ''
        if not multiple:
            colour_description = description
        self.colour_widget = ipywidgets.ColorPicker(
            value=default_colour, description=colour_description)

        # Final widget
        super(ColourSelectionWidget, self).__init__(
            children=[self.labels_box, self.colour_widget])
        self.orientation = 'horizontal'
        self.align = 'start'

        # Assign output
        self.selected_values = {'colour': colours_list, 'labels': labels}

        # Set functionality
        def apply_to_all_function(name):
            tmp = self.colour_widget.value
            for idx in range(len(self.selected_values['colour'])):
                self.selected_values['colour'][idx] = tmp
            self.label_dropdown.value = 0
            if self._render_function is not None:
                self._render_function('', True)
        self.apply_to_all_button.on_click(apply_to_all_function)

        def update_colour_wrt_label(name, value):
            # temporarily remove render_function from r, g, b traits
            self.colour_widget.on_trait_change(self._render_function, 'value',
                                               remove=True)
            # update colour widgets
            self.colour_widget.value = decode_colour(
                self.selected_values['colour'][value])
            # re-assign render_function
            self.colour_widget.on_trait_change(self._render_function, 'value')
        self.label_dropdown.on_trait_change(update_colour_wrt_label, 'value')

        def save_colour(name, value):
            idx = self.label_dropdown.value
            self.selected_values['colour'][idx] = str(self.colour_widget.value)
        self.colour_widget.on_trait_change(save_colour, 'value')

        # Set render function
        self._render_function = None
        self._apply_to_all_render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', label_colour=None, label_background_colour=None,
              picker_colour=None, picker_background_colour=None,
              apply_to_all_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the cornerns of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        label_colour : `str`, optional
            The text colour of the labels dropdown selection.
        label_background_colour : `str`, optional
            The background colour of the labels dropdown selection.
        picker_colour : `str`, optional
            The text colour of the colour picker.
        picker_background_colour : `str`, optional
            The background colour of the colour picker.
        apply_to_all_style : `str`,
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.label_dropdown, font_family, font_size, font_style,
                    font_weight)
        format_font(self.apply_to_all_button, font_family, font_size,
                    font_style, font_weight)
        format_font(self.colour_widget, font_family, font_size, font_style,
                    font_weight)
        format_text_box(self.label_dropdown, label_colour,
                        label_background_colour)
        format_text_box(self.colour_widget, picker_colour,
                        picker_background_colour)
        self.apply_to_all_button.button_style = apply_to_all_style

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        self._apply_to_all_render_function = None
        if self._render_function is not None:
            self.colour_widget.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.colour_widget.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, colours_list, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `colours_list` and `labels` values are different than
        `self.selected_values()`.

        Parameters
        ----------
        colours_list : `list` of `str` or [`float`, `float`, `float`]
            If `str`, it must either a hex code or a colour name, such as ::

                {'blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
                'black', 'white'}

            If [`float`, `float`, `float`], it defines an RGB value and must have
            length 3.
        labels : `list` or ``None``, optional
            A `list` with the labels' names. If ``None``, then a `list` of the
            form ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if labels is None:
            labels = ["label {}".format(k) for k in range(len(colours_list))]

        sel_colours = self.selected_values['colour']
        sel_labels = self.selected_values['labels']
        if (lists_are_the_same(sel_colours, colours_list) and
                not lists_are_the_same(sel_labels, labels)):
            # the provided colours are the same, but the labels changed, so
            # update the labels
            self.selected_values['labels'] = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
        elif (not lists_are_the_same(sel_colours, colours_list) and
              lists_are_the_same(sel_labels, labels)):
            # the provided labels are the same, but the colours are different
            # assign colour
            self.selected_values['colour'] = colours_list
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # update colour widgets
            k = self.label_dropdown.value
            self.colour_widget.value = decode_colour(colours_list[k])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)
        elif (not lists_are_the_same(sel_colours, colours_list) and
              not lists_are_the_same(sel_labels, labels)):
            # both the colours and the labels are different
            self.labels_box.visible = len(labels) > 1
            if len(labels) > 1:
                self.colour_widget.description = ''
            else:
                self.colour_widget.description = self.description
            self.selected_values['colour'] = colours_list
            self.selected_values['labels'] = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
            else:
                self.label_dropdown.value = 0
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # update colour widgets
            self.colour_widget.value = decode_colour(colours_list[0])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)


class ZoomOneScaleWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting zoom options with a single scale.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    zoom_options : `dict`
        The dictionary with the default options. For example ::

            zoom_options = {'min': 0.1, 'max': 4., 'step': 0.05, 'zoom': 1.}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    update_function : `function` or ``None``, optional
        The update function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is realised.
    """
    def __init__(self, zoom_options, render_function=None, update_function=None,
                 description='Figure scale: ', minus_description='fa-minus',
                 plus_description='fa-plus', continuous_update=False):
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(description=m_description,
                                              icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(description=p_description,
                                             icon=p_icon, width='1cm')
        self.zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom'], min=zoom_options['min'],
            max=zoom_options['max'], readout=False, width='6cm',
            continuous_update=continuous_update)
        self.zoom_text = ipywidgets.FloatText(
            value=zoom_options['zoom'], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')
        super(ZoomOneScaleWidget, self).__init__(
            children=[self.title, self.button_minus, self.zoom_slider,
                      self.button_plus, self.zoom_text])
        self.orientation = 'horizontal'
        self.align = 'start'

        # Link the zoom text and slider
        ipywidgets.jslink((self.zoom_slider, 'value'),
                          (self.zoom_text, 'value'))

        # Assign output
        self.selected_values = zoom_options

        # Set functionality
        def value_plus(name):
            tmp_val = float(self.zoom_text.value) + self.selected_values['step']
            if tmp_val > self.selected_values['max']:
                self.zoom_text.value = "{:.2f}".format(
                    self.selected_values['max'])
            else:
                self.zoom_text.value = "{:.2f}".format(tmp_val)
        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = float(self.zoom_text.value) - self.selected_values['step']
            if tmp_val < self.selected_values['min']:
                self.zoom_text.value = "{:.2f}".format(
                    self.selected_values['min'])
            else:
                self.zoom_text.value = "{:.2f}".format(tmp_val)
        self.button_minus.on_click(value_minus)

        def save_zoom_slider(name, value):
            self.selected_values['zoom'] = value
        self.zoom_slider.on_trait_change(save_zoom_slider, 'value')

        def save_zoom_text(name, value):
            self.selected_values['zoom'] = float(value)
        self.zoom_text.on_trait_change(save_zoom_text, 'value')

        # Set render and update functions
        self._update_function = None
        self.add_update_function(update_function)
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', minus_style='', plus_style='',
              text_colour=None, text_background_colour=None, slider_width='6cm',
              slider_bar_colour=None, slider_handle_colour=None,
              slider_text_visible=True):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        minus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        plus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        text_colour : `str`, optional
            The text colour of the index text.
        text_background_colour : `str`, optional
            The background colour of the index text.
        slider_width : `float`, optional
            The width of the slider
        slider_bar_colour : `str`, optional
            The colour of the slider's bar.
        slider_handle_colour : `str`, optional
            The colour of the slider's handle.
        slider_text_visible : `bool`, optional
            Whether the selected value of the slider is visible.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.zoom_text, font_family, font_size, font_style,
                    font_weight)
        self.button_minus.button_style = minus_style
        self.button_plus.button_style = plus_style
        format_text_box(self.zoom_text, text_colour, text_background_colour)
        format_slider(self.zoom_slider, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=slider_text_visible)
        self.zoom_slider.readout = False

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.zoom_slider.on_trait_change(self._render_function, 'value')
            self.zoom_text.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.zoom_slider.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.zoom_text.on_trait_change(self._render_function, 'value',
                                       remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def add_update_function(self, update_function):
        r"""
        Method that adds a `update_function()` to the widget. The signature of
        the given function is also stored in `self._update_function`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._update_function = update_function
        if self._update_function is not None:
            self.zoom_slider.on_trait_change(self._update_function, 'value')
            self.zoom_text.on_trait_change(self._update_function, 'value')

    def remove_update_function(self):
        r"""
        Method that removes the current `self._update_function()` from the
        widget and sets ``self._update_function = None``.
        """
        self.zoom_slider.on_trait_change(self._update_function, 'value',
                                         remove=True)
        self.zoom_text.on_trait_change(self._update_function, 'value',
                                       remove=True)
        self._update_function = None

    def replace_update_function(self, update_function):
        r"""
        Method that replaces the current `self._update_function()` of the widget
        with the given `update_function()`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_update_function()

        # add new function
        self.add_update_function(update_function)

    def set_widget_state(self, zoom_options, continuous_update=False,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        zoom_options : `dict`
            The dictionary with the selected options. For example ::

                zoom_options = {'min': 0.1, 'max': 4., 'step': 0.05, 'zoom': 1.}

        continuous_update : `bool`, optional
            If ``True``, then the render and update functions are called while
            moving the zoom slider's handle. If ``False``, then the the
            functions are called only when the handle (mouse click) is realised.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # update the continuous update property of the zoom slider
        self.zoom_slider.continuous_update = continuous_update

        # Check if update is required
        if zoom_options != self.selected_values:
            # temporarily remove render and update functions
            render_function = self._render_function
            update_function = self._update_function
            self.remove_render_function()
            self.remove_update_function()

            # update widgets
            self.zoom_text.min = zoom_options['min']
            self.zoom_slider.min = zoom_options['min']
            self.zoom_text.max = zoom_options['max']
            self.zoom_slider.max = zoom_options['max']
            self.zoom_text.value = "{:.2f}".format(zoom_options['zoom'])

            # re-assign render and update callbacks
            self.add_update_function(update_function)
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = zoom_options


class ZoomTwoScalesWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting zoom options with a single scale.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    zoom_options : `dict`
        The dictionary with the default options. For example ::

            zoom_options = {'zoom_x': 1., 'zoom_y': 1.,
                            'min': 0.1, 'max': 4., 'step': 0.05,
                            'lock_aspect_ratio': False}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    update_function : `function` or ``None``, optional
        The update function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is realised.
    """
    def __init__(self, zoom_options, render_function=None, update_function=None,
                 description='Figure scale: ', minus_description='fa-minus',
                 plus_description='fa-plus', continuous_update=False):
        # titles
        self.title = ipywidgets.Latex(value=description, padding=6, margin=6)
        self.x_title = ipywidgets.Latex(value='X', padding=6, margin=6)
        self.y_title = ipywidgets.Latex(value='Y', padding=6, margin=6)

        # buttons
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.x_button_minus = ipywidgets.Button(description=m_description,
                                                icon=m_icon, width='1cm')
        self.y_button_minus = ipywidgets.Button(description=m_description,
                                                icon=m_icon, width='1cm')
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.x_button_plus = ipywidgets.Button(description=p_description,
                                               icon=p_icon, width='1cm')
        self.y_button_plus = ipywidgets.Button(description=p_description,
                                               icon=p_icon, width='1cm')

        # sliders and texts
        self.x_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom_x'], min=zoom_options['min'],
            max=zoom_options['max'], readout=False, width='6cm',
            continuous_update=continuous_update)
        self.y_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options['zoom_y'], min=zoom_options['min'],
            max=zoom_options['max'], readout=False, width='6cm',
            continuous_update=continuous_update)
        self.x_zoom_text = ipywidgets.FloatText(
            value=zoom_options['zoom_x'], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')
        self.y_zoom_text = ipywidgets.FloatText(
            value=zoom_options['zoom_y'], min=zoom_options['min'],
            max=zoom_options['max'], width='1.5cm')

        # x and y boxes
        self.x_box = ipywidgets.HBox(
            children=[self.x_title, self.x_button_minus, self.x_zoom_slider,
                      self.x_button_plus, self.x_zoom_text], margin='0.05cm')
        self.y_box = ipywidgets.HBox(
            children=[self.y_title, self.y_button_minus, self.y_zoom_slider,
                      self.y_button_plus, self.y_zoom_text], margin='0.05cm')
        self.x_y_box = ipywidgets.VBox(children=[self.x_box, self.y_box])

        # link button
        self.lock_link = ipywidgets.jslink((self.x_zoom_slider, 'value'),
                                           (self.y_zoom_slider, 'value'))
        lock_icon = 'fa-link'
        if not zoom_options['lock_aspect_ratio']:
            lock_icon = 'fa-unlink'
            self.lock_link.unlink()
        self.lock_aspect_button = ipywidgets.ToggleButton(
            value=zoom_options['lock_aspect_ratio'], description='',
            icon=lock_icon)
        self.options_box = ipywidgets.HBox(
            children=[self.lock_aspect_button, self.x_y_box], align='center')

        super(ZoomTwoScalesWidget, self).__init__(
            children=[self.title, self.options_box])
        self.orientation = 'horizontal'
        self.align = 'center'

        # Link the zoom texts and sliders
        ipywidgets.jslink((self.x_zoom_slider, 'value'),
                          (self.x_zoom_text, 'value'))
        ipywidgets.jslink((self.y_zoom_slider, 'value'),
                          (self.y_zoom_text, 'value'))

        # Assign output
        self.selected_values = zoom_options

        # Set functionality
        def x_value_plus(name):
            tmp_val = float(self.x_zoom_text.value) + self.selected_values[
                'step']
            if tmp_val > self.selected_values['max']:
                self.x_zoom_text.value = "{:.2f}".format(
                    self.selected_values['max'])
            else:
                self.x_zoom_text.value = "{:.2f}".format(tmp_val)
        self.x_button_plus.on_click(x_value_plus)

        def x_value_minus(name):
            tmp_val = float(self.x_zoom_text.value) - self.selected_values[
                'step']
            if tmp_val < self.selected_values['min']:
                self.x_zoom_text.value = "{:.2f}".format(
                    self.selected_values['min'])
            else:
                self.x_zoom_text.value = "{:.2f}".format(tmp_val)
        self.x_button_minus.on_click(x_value_minus)

        def y_value_plus(name):
            tmp_val = float(self.y_zoom_text.value) + self.selected_values[
                'step']
            if tmp_val > self.selected_values['max']:
                self.y_zoom_text.value = "{:.2f}".format(
                    self.selected_values['max'])
            else:
                self.y_zoom_text.value = "{:.2f}".format(tmp_val)
        self.y_button_plus.on_click(y_value_plus)

        def y_value_minus(name):
            tmp_val = float(self.y_zoom_text.value) - self.selected_values[
                'step']
            if tmp_val < self.selected_values['min']:
                self.y_zoom_text.value = "{:.2f}".format(
                    self.selected_values['min'])
            else:
                self.y_zoom_text.value = "{:.2f}".format(tmp_val)
        self.y_button_minus.on_click(y_value_minus)

        def x_save_zoom_slider(name, value):
            self.selected_values['zoom_x'] = value
            if self.selected_values['lock_aspect_ratio']:
                self.selected_values['zoom_y'] = value
        self.x_zoom_slider.on_trait_change(x_save_zoom_slider, 'value')

        def x_save_zoom_text(name, value):
            self.selected_values['zoom_x'] = float(value)
            if self.selected_values['lock_aspect_ratio']:
                self.selected_values['zoom_y'] = float(value)
        self.x_zoom_text.on_trait_change(x_save_zoom_text, 'value')

        def y_save_zoom_slider(name, value):
            self.selected_values['zoom_y'] = value
            if self.selected_values['lock_aspect_ratio']:
                self.selected_values['zoom_x'] = value
        self.y_zoom_slider.on_trait_change(y_save_zoom_slider, 'value')

        def y_save_zoom_text(name, value):
            self.selected_values['zoom_y'] = float(value)
            if self.selected_values['lock_aspect_ratio']:
                self.selected_values['zoom_x'] = float(value)
        self.y_zoom_text.on_trait_change(y_save_zoom_text, 'value')

        def link_button(name, value):
            self.selected_values['lock_aspect_ratio'] = value
            if value:
                self.lock_aspect_button.icon = 'fa-link'
                self.lock_link = ipywidgets.jslink(
                    (self.x_zoom_slider, 'value'),
                    (self.y_zoom_slider, 'value'))
                self.selected_values['zoom_y'] = self.selected_values['zoom_x']
            else:
                self.lock_aspect_button.icon = 'fa-unlink'
                self.lock_link.unlink()
        self.lock_aspect_button.on_trait_change(link_button, 'value')

        # Set render and update functions
        self._update_function = None
        self.add_update_function(update_function)
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', minus_style='', plus_style='', lock_style='',
              text_colour=None, text_background_colour=None, slider_width='6cm',
              slider_bar_colour=None, slider_handle_colour=None,
              slider_text_visible=True):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        minus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        plus_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        text_colour : `str`, optional
            The text colour of the index text.
        text_background_colour : `str`, optional
            The background colour of the index text.
        slider_width : `float`, optional
            The width of the slider
        slider_bar_colour : `str`, optional
            The colour of the slider's bar.
        slider_handle_colour : `str`, optional
            The colour of the slider's handle.
        slider_text_visible : `bool`, optional
            Whether the selected value of the slider is visible.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.x_zoom_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_button_minus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_button_plus, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_zoom_text, font_family, font_size, font_style,
                    font_weight)
        self.x_button_minus.button_style = minus_style
        self.x_button_plus.button_style = plus_style
        self.y_button_minus.button_style = minus_style
        self.y_button_plus.button_style = plus_style
        self.lock_aspect_button.button_style = lock_style
        format_text_box(self.x_zoom_text, text_colour, text_background_colour)
        format_text_box(self.y_zoom_text, text_colour, text_background_colour)
        format_slider(self.x_zoom_slider, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=slider_text_visible)
        self.x_zoom_slider.readout = False
        format_slider(self.y_zoom_slider, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=slider_text_visible)
        self.y_zoom_slider.readout = False

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.x_zoom_slider.on_trait_change(self._render_function, 'value')
            self.x_zoom_text.on_trait_change(self._render_function, 'value')
            self.y_zoom_slider.on_trait_change(self._render_function, 'value')
            self.y_zoom_text.on_trait_change(self._render_function, 'value')
            self.lock_aspect_button.on_trait_change(self._render_function,
                                                    'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.x_zoom_slider.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self.x_zoom_text.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.y_zoom_slider.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self.y_zoom_text.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.lock_aspect_button.on_trait_change(self._render_function, 'value',
                                                remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def add_update_function(self, update_function):
        r"""
        Method that adds a `update_function()` to the widget. The signature of
        the given function is also stored in `self._update_function`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._update_function = update_function
        if self._update_function is not None:
            self.x_zoom_slider.on_trait_change(self._update_function, 'value')
            self.x_zoom_text.on_trait_change(self._update_function, 'value')
            self.y_zoom_slider.on_trait_change(self._update_function, 'value')
            self.y_zoom_text.on_trait_change(self._update_function, 'value')
            self.lock_aspect_button.on_trait_change(self._update_function,
                                                    'value')

    def remove_update_function(self):
        r"""
        Method that removes the current `self._update_function()` from the
        widget and sets ``self._update_function = None``.
        """
        self.x_zoom_slider.on_trait_change(self._update_function, 'value',
                                           remove=True)
        self.x_zoom_text.on_trait_change(self._update_function, 'value',
                                         remove=True)
        self.y_zoom_slider.on_trait_change(self._update_function, 'value',
                                           remove=True)
        self.y_zoom_text.on_trait_change(self._update_function, 'value',
                                         remove=True)
        self.lock_aspect_button.on_trait_change(self._update_function, 'value',
                                                remove=True)
        self._update_function = None

    def replace_update_function(self, update_function):
        r"""
        Method that replaces the current `self._update_function()` of the widget
        with the given `update_function()`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_update_function()

        # add new function
        self.add_update_function(update_function)

    def set_widget_state(self, zoom_options, continuous_update=False,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        zoom_options : `dict`
            The dictionary with the selected options. For example ::

            zoom_options = {'zoom_x': 1., 'zoom_y': 1.,
                            'min': 0.1, 'max': 4., 'step': 0.05,
                            'lock_aspect_ratio': False}

        continuous_update : `bool`, optional
            If ``True``, then the render and update functions are called while
            moving the zoom slider's handle. If ``False``, then the the
            functions are called only when the handle (mouse click) is realised.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # update the continuous update property of the zoom sliders
        self.x_zoom_slider.continuous_update = continuous_update
        self.y_zoom_slider.continuous_update = continuous_update

        # Check if update is required
        if zoom_options != self.selected_values:
            # temporarily remove render and update functions
            render_function = self._render_function
            update_function = self._update_function
            self.remove_render_function()
            self.remove_update_function()

            # update widgets
            self.x_zoom_text.min = zoom_options['min']
            self.x_zoom_slider.min = zoom_options['min']
            self.y_zoom_text.min = zoom_options['min']
            self.y_zoom_slider.min = zoom_options['min']
            self.x_zoom_text.max = zoom_options['max']
            self.x_zoom_slider.max = zoom_options['max']
            self.y_zoom_text.max = zoom_options['max']
            self.y_zoom_slider.max = zoom_options['max']
            if zoom_options['lock_aspect_ratio']:
                zoom_options['zoom_y'] = zoom_options['zoom_x']
            self.x_zoom_text.value = "{:.2f}".format(zoom_options['zoom_x'])
            self.y_zoom_text.value = "{:.2f}".format(zoom_options['zoom_y'])
            self.lock_aspect_button.value = zoom_options['lock_aspect_ratio']

            # re-assign render and update callbacks
            self.add_update_function(update_function)
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = zoom_options


class ImageOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting image rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    image_options : `dict`
        The initial image options. Example ::

            image_options = {'alpha': 1.,
                             'interpolation': 'bilinear',
                             'cmap_name': 'gray'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, image_options, render_function=None):
        # Create widgets
        self.interpolation_checkbox = ipywidgets.Checkbox(
            description='Pixelated',
            value=image_options['interpolation'] == 'none')
        self.alpha_slider = ipywidgets.FloatSlider(
            description='Alpha', value=image_options['alpha'],
            min=0.0, max=1.0, step=0.05, width='4cm', continuous_update=False)
        cmap_dict = OrderedDict()
        cmap_dict['None'] = None
        cmap_dict['afmhot'] = 'afmhot'
        cmap_dict['autumn'] = 'autumn'
        cmap_dict['binary'] = 'binary'
        cmap_dict['bone'] = 'bone'
        cmap_dict['brg'] = 'brg'
        cmap_dict['bwr'] = 'bwr'
        cmap_dict['cool'] = 'cool'
        cmap_dict['coolwarm'] = 'coolwarm'
        cmap_dict['copper'] = 'copper'
        cmap_dict['cubehelix']= 'cubehelix'
        cmap_dict['flag'] = 'flag'
        cmap_dict['gist_earth'] = 'gist_earth'
        cmap_dict['gist_heat'] = 'gist_heat'
        cmap_dict['gist_gray'] = 'gist_gray'
        cmap_dict['gist_ncar'] = 'gist_ncar'
        cmap_dict['gist_rainbow'] = 'gist_rainbow'
        cmap_dict['gist_stern'] = 'gist_stern'
        cmap_dict['gist_yarg'] = 'gist_yarg'
        cmap_dict['gnuplot'] = 'gnuplot'
        cmap_dict['gnuplot2'] = 'gnuplot2'
        cmap_dict['gray'] = 'gray'
        cmap_dict['hot'] = 'hot'
        cmap_dict['hsv'] = 'hsv'
        cmap_dict['jet'] = 'jet'
        cmap_dict['nipy_spectral'] = 'nipy_spectral'
        cmap_dict['ocean'] = 'ocean'
        cmap_dict['pink'] = 'pink'
        cmap_dict['prism'] = 'prism'
        cmap_dict['rainbow'] = 'rainbow'
        cmap_dict['seismic'] = 'seismic'
        cmap_dict['spectral'] = 'spectral'
        cmap_dict['spring'] = 'spring'
        cmap_dict['summer'] = 'summer'
        cmap_dict['terrain'] = 'terrain'
        cmap_dict['winter'] = 'winter'
        self.cmap_select = ipywidgets.Select(
            options=cmap_dict, value='gray', description='Colourmap',
            width='3cm', height='2cm')
        self.alpha_interpolation_box = ipywidgets.VBox(children=[
            self.alpha_slider, self.interpolation_checkbox])
        super(ImageOptionsWidget, self).__init__(
            children=[self.cmap_select, self.alpha_interpolation_box])
        self.align = 'start'
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = image_options

        # Set functionality
        def save_interpolation(name, value):
            if value:
                self.selected_values['interpolation'] = 'none'
            else:
                self.selected_values['interpolation'] = 'bilinear'
        self.interpolation_checkbox.on_trait_change(save_interpolation, 'value')

        def save_alpha(name, value):
            self.selected_values['alpha'] = value
        self.alpha_slider.on_trait_change(save_alpha, 'value')

        def save_cmap(name, value):
            self.selected_values['cmap_name'] = value
        self.cmap_select.on_trait_change(save_cmap, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', alpha_handle_colour=None,
              alpha_bar_colour=None, cmap_colour=None,
              cmap_background_colour=None):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        alpha_handle_colour : `str`, optional
            The colour of the handle of alpha slider.
        alpha_bar_colour : `str`, optional
            The colour of the bar of alpha slider.
        cmap_colour : `str`, optional
            The text colour of the cmap selector.
        cmap_background_colour : `str`, optional
            The background colour of the cmap selector.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.alpha_slider, font_family, font_size, font_style,
                    font_weight)
        format_font(self.interpolation_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cmap_select, font_family, font_size, font_style,
                    font_weight)
        format_slider(self.alpha_slider, slider_width='4cm',
                      slider_handle_colour=alpha_handle_colour,
                      slider_bar_colour=alpha_bar_colour,
                      slider_text_visible=True)
        format_text_box(self.cmap_select, cmap_colour, cmap_background_colour)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.interpolation_checkbox.on_trait_change(self._render_function,
                                                        'value')
            self.alpha_slider.on_trait_change(self._render_function, 'value')
            self.cmap_select.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.interpolation_checkbox.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.alpha_slider.on_trait_change(self._render_function, 'value',
                                          remove=True)
        self.cmap_select.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, image_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        image_options : `dict`
            The image options. Example ::

                image_options = {'alpha': 1.,
                                 'interpolation': 'bilinear',
                                 'cmap_name': 'gray'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if image_options != self.selected_values:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.alpha_slider.value = image_options['alpha']
            self.interpolation_checkbox.value = \
                image_options['interpolation'] == 'none'
            self.cmap_select.value = image_options['cmap_name']

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = image_options


class LineOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting line rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    line_options : `dict`
        The initial line options. Example ::

            line_options = {'render_lines': True, 'line_width': 1,
                            'line_colour': ['blue'], 'line_style': '-'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    labels : `list` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """
    def __init__(self, line_options, render_function=None,
                 render_checkbox_title='Render lines', labels=None):
        self.render_lines_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=line_options['render_lines'])
        self.line_width_text = ipywidgets.BoundedFloatText(
            description='Width', value=line_options['line_width'], min=0.,
            max=10**6)
        line_style_dict = OrderedDict()
        line_style_dict['solid'] = '-'
        line_style_dict['dashed'] = '--'
        line_style_dict['dash-dot'] = '-.'
        line_style_dict['dotted'] = ':'
        self.line_style_dropdown = ipywidgets.Dropdown(
            options=line_style_dict, value=line_options['line_style'],
            description='Style')
        self.line_colour_widget = ColourSelectionWidget(
            line_options['line_colour'], description='Colour', labels=labels,
            render_function=render_function)
        self.line_options_box = ipywidgets.Box(
            children=[self.line_style_dropdown, self.line_width_text,
                      self.line_colour_widget])
        super(LineOptionsWidget, self).__init__(
            children=[self.render_lines_checkbox, self.line_options_box])
        self.align = 'start'
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = line_options

        # Set functionality
        def line_options_visible(name, value):
            self.line_options_box.visible = value
        line_options_visible('', line_options['render_lines'])
        self.render_lines_checkbox.on_trait_change(line_options_visible,
                                                   'value')

        def save_render_lines(name, value):
            self.selected_values['render_lines'] = value
        self.render_lines_checkbox.on_trait_change(save_render_lines, 'value')

        def save_line_width(name, value):
            self.selected_values['line_width'] = float(value)
        self.line_width_text.on_trait_change(save_line_width, 'value')

        def save_line_style(name, value):
            self.selected_values['line_style'] = value
        self.line_style_dropdown.on_trait_change(save_line_style, 'value')

        self.selected_values['line_colour'] = \
            self.line_colour_widget.selected_values['colour']

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_lines_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.line_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.line_width_text, font_family, font_size, font_style,
                    font_weight)
        self.line_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.render_lines_checkbox.on_trait_change(self._render_function,
                                                       'value')
            self.line_style_dropdown.on_trait_change(self._render_function,
                                                     'value')
            self.line_width_text.on_trait_change(self._render_function, 'value')
        self.line_colour_widget.add_render_function(render_function)

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.render_lines_checkbox.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.line_style_dropdown.on_trait_change(self._render_function, 'value',
                                                 remove=True)
        self.line_width_text.on_trait_change(self._render_function, 'value',
                                             remove=True)
        self.line_colour_widget.remove_render_function()
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, line_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        line_options : `dict`
            The new set of options. For example ::

                line_options = {'render_lines': True,
                                'line_width': 2,
                                'line_colour': ['red'],
                                'line_style': '-'}

        labels : `list` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != line_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_lines_checkbox.value = line_options['render_lines']
            self.line_style_dropdown.value = line_options['line_style']
            self.line_width_text.value = float(line_options['line_width'])

            # re-assign render callback
            self.add_render_function(render_function)

            # update line_colour
            self.line_colour_widget.set_widget_state(
                line_options['line_colour'], labels=labels,
                allow_callback=False)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = line_options


class MarkerOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting marker rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    marker_options : `dict`
        The initial marker options. Example ::

            marker_options = {'render_markers': True,
                              'marker_size': 20,
                              'marker_face_colour': ['red'],
                              'marker_edge_colour': ['black'],
                              'marker_style': 'o',
                              'marker_edge_width': 1}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render marker checkbox.
    labels : `list` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """
    def __init__(self, marker_options, render_function=None,
                 render_checkbox_title='Render markers', labels=None):
        self.render_markers_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=marker_options['render_markers'])
        self.marker_size_text = ipywidgets.BoundedIntText(
            description='Size', value=marker_options['marker_size'], min=0,
            max=10**6)
        self.marker_edge_width_text = ipywidgets.BoundedFloatText(
            description='Edge width', min=0., max=10**6,
            value=marker_options['marker_edge_width'])
        marker_style_dict = OrderedDict()
        marker_style_dict['point'] = '.'
        marker_style_dict['pixel'] = ','
        marker_style_dict['circle'] = 'o'
        marker_style_dict['triangle down'] = 'v'
        marker_style_dict['triangle up'] = '^'
        marker_style_dict['triangle left'] = '<'
        marker_style_dict['triangle right'] = '>'
        marker_style_dict['tri down'] = '1'
        marker_style_dict['tri up'] = '2'
        marker_style_dict['tri left'] = '3'
        marker_style_dict['tri right'] = '4'
        marker_style_dict['octagon'] = '8'
        marker_style_dict['square'] = 's'
        marker_style_dict['pentagon'] = 'p'
        marker_style_dict['star'] = '*'
        marker_style_dict['hexagon 1'] = 'h'
        marker_style_dict['hexagon 2'] = 'H'
        marker_style_dict['plus'] = '+'
        marker_style_dict['x'] = 'x'
        marker_style_dict['diamond'] = 'D'
        marker_style_dict['thin diamond'] = 'd'
        self.marker_style_dropdown = ipywidgets.Dropdown(
            options=marker_style_dict, value=marker_options['marker_style'],
            description='Style')
        self.marker_box_1 = ipywidgets.VBox(
            children=[self.marker_style_dropdown, self.marker_size_text,
                      self.marker_edge_width_text], margin='0.1cm')
        self.marker_face_colour_widget = ColourSelectionWidget(
            marker_options['marker_face_colour'], description='Face colour',
            labels=labels, render_function=render_function)
        self.marker_edge_colour_widget = ColourSelectionWidget(
            marker_options['marker_edge_colour'], description='Edge colour',
            labels=labels, render_function=render_function)
        self.marker_box_2 = ipywidgets.VBox(
            children=[self.marker_face_colour_widget,
                      self.marker_edge_colour_widget], margin='0.1cm',
            align='end')
        self.marker_options_box = ipywidgets.HBox(
            children=[self.marker_box_1, self.marker_box_2])
        super(MarkerOptionsWidget, self).__init__(children=[
            self.render_markers_checkbox, self.marker_options_box])
        self.align = 'start'
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = marker_options

        # Set functionality
        def marker_options_visible(name, value):
            self.marker_options_box.visible = value
        marker_options_visible('', marker_options['render_markers'])
        self.render_markers_checkbox.on_trait_change(marker_options_visible,
                                                     'value')

        def save_render_markers(name, value):
            self.selected_values['render_markers'] = value
        self.render_markers_checkbox.on_trait_change(save_render_markers,
                                                     'value')

        def save_marker_size(name, value):
            self.selected_values['marker_size'] = int(value)
        self.marker_size_text.on_trait_change(save_marker_size, 'value')

        def save_marker_edge_width(name, value):
            self.selected_values['marker_edge_width'] = float(value)
        self.marker_edge_width_text.on_trait_change(save_marker_edge_width,
                                                    'value')

        def save_marker_style(name, value):
            self.selected_values['marker_style'] = value
        self.marker_style_dropdown.on_trait_change(save_marker_style, 'value')

        self.selected_values['marker_edge_colour'] = \
            self.marker_edge_colour_widget.selected_values['colour']
        self.selected_values['marker_face_colour'] = \
            self.marker_face_colour_widget.selected_values['colour']

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_markers_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.marker_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.marker_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.marker_edge_width_text, font_family, font_size,
                    font_style, font_weight)
        self.marker_edge_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')
        self.marker_face_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.render_markers_checkbox.on_trait_change(self._render_function,
                                                         'value')
            self.marker_style_dropdown.on_trait_change(self._render_function,
                                                       'value')
            self.marker_edge_width_text.on_trait_change(self._render_function,
                                                        'value')
            self.marker_size_text.on_trait_change(self._render_function,
                                                  'value')
        self.marker_edge_colour_widget.add_render_function(render_function)
        self.marker_face_colour_widget.add_render_function(render_function)

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.render_markers_checkbox.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.marker_style_dropdown.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.marker_edge_width_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.marker_size_text.on_trait_change(self._render_function, 'value',
                                              remove=True)
        self.marker_edge_colour_widget.remove_render_function()
        self.marker_face_colour_widget.remove_render_function()
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, marker_options, labels=None,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        marker_options : `dict`
            The new set of options. For example ::

                marker_options = {'render_markers': True,
                                  'marker_size': 20,
                                  'marker_face_colour': ['red'],
                                  'marker_edge_colour': ['black'],
                                  'marker_style': 'o',
                                  'marker_edge_width': 1}

        labels : `list` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != marker_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_markers_checkbox.value = marker_options['render_markers']
            self.marker_style_dropdown.value = marker_options['marker_style']
            self.marker_size_text.value = int(marker_options['marker_size'])
            self.marker_edge_width_text.value = \
                float(marker_options['marker_edge_width'])

            # re-assign render callback
            self.add_render_function(render_function)

            # update marker_face_colour
            self.marker_face_colour_widget.set_widget_state(
                marker_options['marker_face_colour'], labels=labels,
                allow_callback=False)

            # update marker_edge_colour
            self.marker_edge_colour_widget.set_widget_state(
                marker_options['marker_edge_colour'], labels=labels,
                allow_callback=False)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = marker_options


class NumberingOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting numbering rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    numbers_options : `dict`
        The initial numbering options. Example ::

            numbers_options = {'render_numbering': True,
                               'numbers_font_name': 'serif',
                               'numbers_font_size': 10,
                               'numbers_font_style': 'normal',
                               'numbers_font_weight': 'normal',
                               'numbers_font_colour': ['black'],
                               'numbers_horizontal_align': 'center',
                               'numbers_vertical_align': 'bottom'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render numbering checkbox.
    """
    def __init__(self, numbers_options, render_function=None,
                 render_checkbox_title='Render numbering'):
        self.render_numbering_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=numbers_options['render_numbering'])
        numbers_font_name_dict = OrderedDict()
        numbers_font_name_dict['serif'] = 'serif'
        numbers_font_name_dict['sans-serif'] = 'sans-serif'
        numbers_font_name_dict['cursive'] = 'cursive'
        numbers_font_name_dict['fantasy'] = 'fantasy'
        numbers_font_name_dict['monospace'] = 'monospace'
        self.numbers_font_name_dropdown = ipywidgets.Dropdown(
            options=numbers_font_name_dict,
            value=numbers_options['numbers_font_name'], description='Font')
        self.numbers_font_size_text = ipywidgets.BoundedIntText(
            description='Size', min=0, max=10**6,
            value=numbers_options['numbers_font_size'])
        numbers_font_style_dict = OrderedDict()
        numbers_font_style_dict['normal'] = 'normal'
        numbers_font_style_dict['italic'] = 'italic'
        numbers_font_style_dict['oblique'] = 'oblique'
        self.numbers_font_style_dropdown = ipywidgets.Dropdown(
            options=numbers_font_style_dict,
            value=numbers_options['numbers_font_style'], description='Style')
        numbers_font_weight_dict = OrderedDict()
        numbers_font_weight_dict['normal'] = 'normal'
        numbers_font_weight_dict['ultralight'] = 'ultralight'
        numbers_font_weight_dict['light'] = 'light'
        numbers_font_weight_dict['regular'] = 'regular'
        numbers_font_weight_dict['book'] = 'book'
        numbers_font_weight_dict['medium'] = 'medium'
        numbers_font_weight_dict['roman'] = 'roman'
        numbers_font_weight_dict['semibold'] = 'semibold'
        numbers_font_weight_dict['demibold'] = 'demibold'
        numbers_font_weight_dict['demi'] = 'demi'
        numbers_font_weight_dict['bold'] = 'bold'
        numbers_font_weight_dict['heavy'] = 'heavy'
        numbers_font_weight_dict['extra bold'] = 'extra bold'
        numbers_font_weight_dict['black'] = 'black'
        self.numbers_font_weight_dropdown = ipywidgets.Dropdown(
            options=numbers_font_weight_dict,
            value=numbers_options['numbers_font_weight'], description='Weight')
        self.numbers_font_colour_widget = ColourSelectionWidget(
            numbers_options['numbers_font_colour'], description='Colour',
            render_function=render_function)
        numbers_horizontal_align_dict = OrderedDict()
        numbers_horizontal_align_dict['center'] = 'center'
        numbers_horizontal_align_dict['right'] = 'right'
        numbers_horizontal_align_dict['left'] = 'left'
        self.numbers_horizontal_align_dropdown = ipywidgets.Dropdown(
            options=numbers_horizontal_align_dict,
            value=numbers_options['numbers_horizontal_align'],
            description='Align hor.')
        numbers_vertical_align_dict = OrderedDict()
        numbers_vertical_align_dict['center'] = 'center'
        numbers_vertical_align_dict['top'] = 'top'
        numbers_vertical_align_dict['bottom'] = 'bottom'
        numbers_vertical_align_dict['baseline'] = 'baseline'
        self.numbers_vertical_align_dropdown = ipywidgets.Dropdown(
            options=numbers_vertical_align_dict,
            value=numbers_options['numbers_vertical_align'],
            description='Align ver.')
        self.name_size_style_weight = ipywidgets.VBox(
            children=[self.numbers_font_name_dropdown,
                      self.numbers_font_size_text,
                      self.numbers_font_style_dropdown,
                      self.numbers_font_weight_dropdown])
        self.colour_horizontal_vertical_align = ipywidgets.VBox(
            children=[self.numbers_font_colour_widget,
                      self.numbers_horizontal_align_dropdown,
                      self.numbers_vertical_align_dropdown])
        self.numbering_options_box = ipywidgets.HBox(
            children=[self.name_size_style_weight,
                      self.colour_horizontal_vertical_align])
        super(NumberingOptionsWidget, self).__init__(
            children=[self.render_numbering_checkbox,
                      self.numbering_options_box])
        self.align = 'start'
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = numbers_options

        # Set functionality
        def numbering_options_visible(name, value):
            self.numbering_options_box.visible = value
        numbering_options_visible('', numbers_options['render_numbering'])
        self.render_numbering_checkbox.on_trait_change(
            numbering_options_visible, 'value')

        def save_render_numbering(name, value):
            self.selected_values['render_numbering'] = value
        self.render_numbering_checkbox.on_trait_change(save_render_numbering,
                                                       'value')

        def save_numbers_font_name(name, value):
            self.selected_values['numbers_font_name'] = value
        self.numbers_font_name_dropdown.on_trait_change(save_numbers_font_name,
                                                        'value')

        def save_numbers_font_size(name, value):
            self.selected_values['numbers_font_size'] = int(value)
        self.numbers_font_size_text.on_trait_change(save_numbers_font_size,
                                                    'value')

        def save_numbers_font_style(name, value):
            self.selected_values['numbers_font_style'] = value
        self.numbers_font_style_dropdown.on_trait_change(
            save_numbers_font_style, 'value')

        def save_numbers_font_weight(name, value):
            self.selected_values['numbers_font_weight'] = value
        self.numbers_font_weight_dropdown.on_trait_change(
            save_numbers_font_weight, 'value')

        def save_numbers_horizontal_align(name, value):
            self.selected_values['numbers_horizontal_align'] = value
        self.numbers_horizontal_align_dropdown.on_trait_change(
            save_numbers_horizontal_align, 'value')

        def save_numbers_vertical_align(name, value):
            self.selected_values['numbers_vertical_align'] = value
        self.numbers_vertical_align_dropdown.on_trait_change(
            save_numbers_vertical_align, 'value')

        self.selected_values['numbers_font_colour'] = \
            self.numbers_font_colour_widget.selected_values['colour']

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_numbering_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.numbers_horizontal_align_dropdown, font_family,
                    font_size, font_style, font_weight)
        format_font(self.numbers_vertical_align_dropdown, font_family,
                    font_size, font_style, font_weight)
        self.numbers_font_colour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style,
            label_colour=None, label_background_colour=None,
            picker_colour=None, picker_background_colour=None,
            apply_to_all_style='')

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.render_numbering_checkbox.on_trait_change(
                self._render_function, 'value')
            self.numbers_font_name_dropdown.on_trait_change(
                self._render_function, 'value')
            self.numbers_font_style_dropdown.on_trait_change(
                self._render_function, 'value')
            self.numbers_font_size_text.on_trait_change(self._render_function,
                                                        'value')
            self.numbers_font_weight_dropdown.on_trait_change(
                self._render_function, 'value')
            self.numbers_horizontal_align_dropdown.on_trait_change(
                self._render_function, 'value')
            self.numbers_vertical_align_dropdown.on_trait_change(
                self._render_function, 'value')
        self.numbers_font_colour_widget.add_render_function(render_function)

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.render_numbering_checkbox.on_trait_change(self._render_function,
                                                       'value', remove=True)
        self.numbers_font_name_dropdown.on_trait_change(self._render_function,
                                                        'value', remove=True)
        self.numbers_font_style_dropdown.on_trait_change(self._render_function,
                                                         'value', remove=True)
        self.numbers_font_size_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.numbers_font_weight_dropdown.on_trait_change(self._render_function,
                                                          'value', remove=True)
        self.numbers_horizontal_align_dropdown.on_trait_change(
            self._render_function, 'value', remove=True)
        self.numbers_vertical_align_dropdown.on_trait_change(
            self._render_function, 'value', remove=True)
        self.numbers_font_colour_widget.remove_render_function()
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, numbers_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        numbers_options : `dict`
            The new set of options. For example ::

                numbers_options = {'render_numbering': True,
                                   'numbers_font_name': 'serif',
                                   'numbers_font_size': 10,
                                   'numbers_font_style': 'normal',
                                   'numbers_font_weight': 'normal',
                                   'numbers_font_colour': ['white'],
                                   'numbers_horizontal_align': 'center',
                                   'numbers_vertical_align': 'bottom'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != numbers_options:
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_numbering_checkbox.value = \
                numbers_options['render_numbering']
            self.numbers_font_name_dropdown.value = \
                numbers_options['numbers_font_name']
            self.numbers_font_size_text.value = \
                int(numbers_options['numbers_font_size'])
            self.numbers_font_style_dropdown.value = \
                numbers_options['numbers_font_style']
            self.numbers_font_weight_dropdown.value = \
                numbers_options['numbers_font_weight']
            self.numbers_horizontal_align_dropdown.value = \
                numbers_options['numbers_horizontal_align']
            self.numbers_vertical_align_dropdown.value = \
                numbers_options['numbers_vertical_align']

            # re-assign render callback
            self.add_render_function(render_function)

            # update numbers_font_colour
            self.numbers_font_colour_widget.set_widget_state(
                numbers_options['numbers_font_colour'],
                allow_callback=False)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = numbers_options


class AxesLimitsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting the axes limits.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and functions of the widget, please refer to the `set_widget_state()`,
    `replace_update_function()` and `replace_render_function()` methods.

    Parameters
    ----------
    axes_limits : `dict`
        The dictionary with the default options. For example ::

            axes_limits = {'x': None, 'y': 0.1, 'x_min': 0, 'x_max': 100,
                           'x_step': 1., 'y_min': 0, 'y_max': 100, 'y_step': 1.}

    render_function : `function` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    update_function : `function` or ``None``, optional
        The update function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, axes_limits, render_function=None, update_function=None):
        # x limits
        if axes_limits['x'] is None:
            toggles_initial_value = 'auto'
            slider_initial_value = 0.
            slider_visible = False
            range_initial_value = [0, 100]
            range_visible = False
        elif isinstance(axes_limits['x'], float):
            toggles_initial_value = 'percentage'
            slider_initial_value = axes_limits['x']
            slider_visible = True
            range_initial_value = [0, 100]
            range_visible = False
        else:
            toggles_initial_value = 'range'
            slider_initial_value = 0.
            slider_visible = False
            range_initial_value = axes_limits['x']
            range_visible = True
        self.axes_x_limits_toggles = ipywidgets.ToggleButtons(
            description='X:', value=toggles_initial_value,
            options=['auto', 'percentage', 'range'], margin='0.2cm')
        self.axes_x_limits_percentage = ipywidgets.FloatSlider(
            min=-1.5, max=1.5, step=0.05, value=slider_initial_value,
            width='4cm', visible=slider_visible, continuous_update=False)
        self.axes_x_limits_range = ipywidgets.FloatRangeSlider(
            value=range_initial_value, width='4cm', visible=range_visible,
            continuous_update=False, min=axes_limits['x_min'],
            max=axes_limits['x_max'], step=axes_limits['x_step'])
        self.axes_x_limits_options_box = ipywidgets.VBox(
            children=[self.axes_x_limits_percentage, self.axes_x_limits_range])
        self.axes_x_limits_box = ipywidgets.HBox(
            children=[self.axes_x_limits_toggles,
                      self.axes_x_limits_options_box], align='center')

        # y limits
        if axes_limits['y'] is None:
            toggles_initial_value = 'auto'
            slider_initial_value = 0.
            slider_visible = False
            range_initial_value = [0, 100]
            range_visible = False
        elif isinstance(axes_limits['y'], float):
            toggles_initial_value = 'percentage'
            slider_initial_value = axes_limits['y']
            slider_visible = True
            range_initial_value = [0, 100]
            range_visible = False
        else:
            toggles_initial_value = 'range'
            slider_initial_value = 0.
            slider_visible = False
            range_initial_value = axes_limits['y']
            range_visible = True
        self.axes_y_limits_toggles = ipywidgets.ToggleButtons(
            description='Y:', value=toggles_initial_value,
            options=['auto', 'percentage', 'range'], margin='0.2cm')
        self.axes_y_limits_percentage = ipywidgets.FloatSlider(
            min=-1.5, max=1.5, step=0.05, value=slider_initial_value,
            width='4cm', visible=slider_visible, continuous_update=False)
        self.axes_y_limits_range = ipywidgets.FloatRangeSlider(
            value=range_initial_value, width='4cm', visible=range_visible,
            continuous_update=False, min=axes_limits['y_min'],
            max=axes_limits['y_max'], step=axes_limits['y_step'])
        self.axes_y_limits_options_box = ipywidgets.VBox(
            children=[self.axes_y_limits_percentage, self.axes_y_limits_range])
        self.axes_y_limits_box = ipywidgets.HBox(
            children=[self.axes_y_limits_toggles,
                      self.axes_y_limits_options_box], align='center')

        super(AxesLimitsWidget, self).__init__(children=[self.axes_x_limits_box,
                                                         self.axes_y_limits_box])
        self.align = 'start'

        # Assign output
        self.selected_values = axes_limits

        # Set functionality
        def x_visibility(name, value):
            if value == 'auto':
                self.axes_x_limits_percentage.visible = False
                self.axes_x_limits_range.visible = False
            elif value == 'percentage':
                self.axes_x_limits_percentage.visible = True
                self.axes_x_limits_range.visible = False
            else:
                self.axes_x_limits_percentage.visible = False
                self.axes_x_limits_range.visible = True
        self.axes_x_limits_toggles.on_trait_change(x_visibility, 'value')

        def get_x_value(name, value):
            if self.axes_x_limits_toggles.value == 'auto':
                self.selected_values['x'] = None
            elif value == 'percentage':
                self.selected_values['x'] = self.axes_x_limits_percentage.value
            else:
                self.selected_values['x'] = list(self.axes_x_limits_range.value)
        self.axes_x_limits_toggles.on_trait_change(get_x_value, 'value')
        self.axes_x_limits_percentage.on_trait_change(get_x_value, 'value')
        self.axes_x_limits_range.on_trait_change(get_x_value, 'value')

        def y_visibility(name, value):
            if value == 'auto':
                self.axes_y_limits_percentage.visible = False
                self.axes_y_limits_range.visible = False
            elif value == 'percentage':
                self.axes_y_limits_percentage.visible = True
                self.axes_y_limits_range.visible = False
            else:
                self.axes_y_limits_percentage.visible = False
                self.axes_y_limits_range.visible = True
        self.axes_y_limits_toggles.on_trait_change(y_visibility, 'value')

        def get_y_value(name, value):
            if self.axes_y_limits_toggles.value == 'auto':
                self.selected_values['y'] = None
            elif value == 'percentage':
                self.selected_values['y'] = self.axes_y_limits_percentage.value
            else:
                self.selected_values['y'] = list(self.axes_y_limits_range.value)
        self.axes_y_limits_toggles.on_trait_change(get_y_value, 'value')
        self.axes_y_limits_percentage.on_trait_change(get_y_value, 'value')
        self.axes_y_limits_range.on_trait_change(get_y_value, 'value')

        # Set render and update functions
        self._update_function = None
        self.add_update_function(update_function)
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', toggles_style='', slider_width='4cm',
              slider_bar_colour=None, slider_handle_colour=None):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : ``{'normal', 'italic', 'oblique'}``, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        toggles_style : `str` or ``None`` (see below), optional
            Style options ::

                {'success', 'info', 'warning', 'danger', 'primary', ''}
                or
                None

        slider_width : `float`, optional
            The width of the slider
        slider_bar_colour : `str`, optional
            The colour of the slider's bar.
        slider_handle_colour : `str`, optional
            The colour of the slider's handle.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self.axes_x_limits_toggles, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_toggles, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_percentage, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_range, font_family, font_size, font_style,
                    font_weight)
        format_font(self.axes_y_limits_percentage, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_range, font_family, font_size, font_style,
                    font_weight)
        self.axes_x_limits_toggles.button_style = toggles_style
        self.axes_y_limits_toggles.button_style = toggles_style
        format_slider(self.axes_x_limits_percentage, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=True)
        format_slider(self.axes_y_limits_percentage, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=True)
        format_slider(self.axes_x_limits_range, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=True)
        format_slider(self.axes_y_limits_range, slider_width=slider_width,
                      slider_handle_colour=slider_handle_colour,
                      slider_bar_colour=slider_bar_colour,
                      slider_text_visible=True)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.axes_x_limits_toggles.on_trait_change(self._render_function,
                                                       'value')
            self.axes_x_limits_percentage.on_trait_change(self._render_function,
                                                          'value')
            self.axes_x_limits_range.on_trait_change(self._render_function,
                                                     'value')
            self.axes_y_limits_toggles.on_trait_change(self._render_function,
                                                       'value')
            self.axes_y_limits_percentage.on_trait_change(self._render_function,
                                                          'value')
            self.axes_y_limits_range.on_trait_change(self._render_function,
                                                     'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.axes_x_limits_toggles.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_x_limits_percentage.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.axes_x_limits_range.on_trait_change(self._render_function,
                                                 'value', remove=True)
        self.axes_y_limits_toggles.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_y_limits_percentage.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.axes_y_limits_range.on_trait_change(self._render_function, 'value',
                                                 remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def add_update_function(self, update_function):
        r"""
        Method that adds a `update_function()` to the widget. The signature of
        the given function is also stored in `self._update_function`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._update_function = update_function
        if self._update_function is not None:
            self.axes_x_limits_toggles.on_trait_change(self._update_function,
                                                       'value')
            self.axes_x_limits_percentage.on_trait_change(self._update_function,
                                                          'value')
            self.axes_x_limits_range.on_trait_change(self._update_function,
                                                     'value')
            self.axes_y_limits_toggles.on_trait_change(self._update_function,
                                                       'value')
            self.axes_y_limits_percentage.on_trait_change(self._update_function,
                                                          'value')
            self.axes_y_limits_range.on_trait_change(self._update_function,
                                                     'value')

    def remove_update_function(self):
        r"""
        Method that removes the current `self._update_function()` from the
        widget and sets ``self._update_function = None``.
        """
        self.axes_x_limits_toggles.on_trait_change(self._update_function,
                                                   'value', remove=True)
        self.axes_x_limits_percentage.on_trait_change(self._update_function,
                                                      'value', remove=True)
        self.axes_x_limits_range.on_trait_change(self._update_function,
                                                 'value', remove=True)
        self.axes_y_limits_toggles.on_trait_change(self._update_function,
                                                   'value', remove=True)
        self.axes_y_limits_percentage.on_trait_change(self._update_function,
                                                      'value', remove=True)
        self.axes_y_limits_range.on_trait_change(self._update_function, 'value',
                                                 remove=True)
        self._update_function = None

    def replace_update_function(self, update_function):
        r"""
        Method that replaces the current `self._update_function()` of the widget
        with the given `update_function()`.

        Parameters
        ----------
        update_function : `function` or ``None``, optional
            The update function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_update_function()

        # add new function
        self.add_update_function(update_function)

    def set_widget_state(self, axes_limits, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values()`.

        Parameters
        ----------
        axes_limits : `dict`
            The dictionary with the selected options. For example ::

                axes_limits = {'x': None, 'y': 0.1, 'x_min': 0, 'x_max': 100,
                               'x_step': 1., 'y_min': 0, 'y_max': 100,
                               'y_step': 1.}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if axes_limits != self.selected_values:
            # temporarily remove render and update functions
            render_function = self._render_function
            update_function = self._update_function
            self.remove_render_function()
            self.remove_update_function()

            # update
            self.axes_x_limits_range.min = axes_limits['x_min']
            self.axes_x_limits_range.max = axes_limits['x_max']
            self.axes_x_limits_range.step = axes_limits['x_step']
            self.axes_y_limits_range.min = axes_limits['y_min']
            self.axes_y_limits_range.max = axes_limits['y_max']
            self.axes_y_limits_range.step = axes_limits['y_step']
            if axes_limits['x'] is None:
                self.axes_x_limits_toggles.value = 'auto'
            elif isinstance(axes_limits['x'], float):
                self.axes_x_limits_toggles.value = 'percentage'
                self.axes_x_limits_percentage.value = axes_limits['x']
            else:
                self.axes_x_limits_toggles.value = 'range'
                self.axes_x_limits_range.value = axes_limits['x']
            if axes_limits['y'] is None:
                self.axes_y_limits_toggles.value = 'auto'
            elif isinstance(axes_limits['y'], float):
                self.axes_y_limits_toggles.value = 'percentage'
                self.axes_x_limits_percentage.value = axes_limits['y']
            else:
                self.axes_y_limits_toggles.value = 'range'
                self.axes_y_limits_range.value = axes_limits['y']

            # re-assign render and update callbacks
            self.add_update_function(update_function)
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self._render_function('', True)

        # Assign output
        self.selected_values = axes_limits


class FigureOptionsOneScaleWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting figure related options. Specifically, it
    consists of:

        1) FloatSlider [`self.figure_scale_slider`]: scale slider
        2) Checkbox [`self.render_axes_checkbox`]: render axes checkbox
        3) Dropdown [`self.axes_font_name_dropdown`]: sets font family
        4) BoundedFloatText [`self.axes_font_size_text`]: sets font size
        5) Dropdown [`self.axes_font_style_dropdown`]: sets font style
        6) Dropdown [`self.axes_font_weight_dropdown`]: sets font weight
        7) FloatText [`self.axes_x_limits_from_text`]: sets x limit from
        8) FloatText [`self.axes_x_limits_to_text`]: sets x limit to
        9) Checkbox [`self.axes_x_limits_enable_checkbox`]: enables x limit
        10) Box [`self.axes_x_limits_from_to_box`]: box that contains (7), (8)
        11) HBox [`self.axes_x_limits_box`]: box that contains (9), (10)
        12) FloatText [`self.axes_y_limits_from_text`]: sets y limit from
        13) FloatText [`self.axes_y_limits_to_text`]: sets y limit to
        14) Checkbox [`self.axes_y_limits_enable_checkbox`]: enables y limit
        15) Box [`self.axes_x_limits_from_to_box`]: box that contains (12), (13)
        16) HBox [`self.axes_x_limits_box`]: box that contains (14), (15)
        17) Box [`self`]: box that contains (1), (2), (3), (4), (5), (6), (11)
            and (16)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    figure_options : `dict`
        The initial figure options. Example ::

            figure_options = {'x_scale': 1.,
                              'y_scale': 1.,
                              'render_axes': True,
                              'axes_font_name': 'serif',
                              'axes_font_size': 10,
                              'axes_font_style': 'normal',
                              'axes_font_weight': 'normal',
                              'axes_x_limits': [0, 100],
                              'axes_y_limits': None}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    figure_scale_bounds : (`float`, `float`), optional
        The range of scales that can be optionally applied to the figure.
    figure_scale_step : `float`, optional
        The step of the scale sliders.
    figure_scale_visible : `bool`, optional
        The visibility of the figure scales sliders.
    show_axes_visible : `bool`, optional
        The visibility of the axes checkbox.
    """
    def __init__(self, figure_options, render_function=None,
                 figure_scale_bounds=(0.1, 4.), figure_scale_step=0.05,
                 figure_scale_visible=True, axes_visible=True):
        self.figure_scale_slider = ipywidgets.FloatSlider(
            description='Figure scale:', value=figure_options['x_scale'],
            min=figure_scale_bounds[0], max=figure_scale_bounds[1],
            step=figure_scale_step, visible=figure_scale_visible)
        self.render_axes_checkbox = ipywidgets.Checkbox(
            description='Render axes', value=figure_options['render_axes'],
            visible=axes_visible)
        axes_font_name_dict = OrderedDict()
        axes_font_name_dict['serif'] = 'serif'
        axes_font_name_dict['sans-serif'] = 'sans-serif'
        axes_font_name_dict['cursive'] = 'cursive'
        axes_font_name_dict['fantasy'] = 'fantasy'
        axes_font_name_dict['monospace'] = 'monospace'
        self.axes_font_name_dropdown = ipywidgets.Dropdown(
            options=axes_font_name_dict, value=figure_options['axes_font_name'],
            description='Font', visible=axes_visible)
        self.axes_font_size_text = ipywidgets.BoundedIntText(
            description='Size', value=figure_options['axes_font_size'],
            min=0, max=10**6, visible=axes_visible)
        axes_font_style_dict = OrderedDict()
        axes_font_style_dict['normal'] = 'normal'
        axes_font_style_dict['italic'] = 'italic'
        axes_font_style_dict['oblique'] = 'oblique'
        self.axes_font_style_dropdown = ipywidgets.Dropdown(
            options=axes_font_style_dict, description='Style',
            value=figure_options['axes_font_style'], visible=axes_visible)
        axes_font_weight_dict = OrderedDict()
        axes_font_weight_dict['normal'] = 'normal'
        axes_font_weight_dict['ultralight'] = 'ultralight'
        axes_font_weight_dict['light'] = 'light'
        axes_font_weight_dict['regular'] = 'regular'
        axes_font_weight_dict['book'] = 'book'
        axes_font_weight_dict['medium'] = 'medium'
        axes_font_weight_dict['roman'] = 'roman'
        axes_font_weight_dict['semibold'] = 'semibold'
        axes_font_weight_dict['demibold'] = 'demibold'
        axes_font_weight_dict['demi'] = 'demi'
        axes_font_weight_dict['bold'] = 'bold'
        axes_font_weight_dict['heavy'] = 'heavy'
        axes_font_weight_dict['extra bold'] = 'extra bold'
        axes_font_weight_dict['black'] = 'black'
        self.axes_font_weight_dropdown = ipywidgets.Dropdown(
            options=axes_font_weight_dict,
            value=figure_options['axes_font_weight'], description='Weight',
            visible=axes_visible)
        if figure_options['axes_x_limits'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 100.
        else:
            tmp1 = True
            tmp2 = figure_options['axes_x_limits'][0]
            tmp3 = figure_options['axes_x_limits'][1]
        self.axes_x_limits_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='X limits')
        self.axes_x_limits_from_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.axes_x_limits_to_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.axes_x_limits_from_to_box = ipywidgets.Box(
            children=[self.axes_x_limits_from_text,
                      self.axes_x_limits_to_text])
        self.axes_x_limits_box = ipywidgets.HBox(
            children=[self.axes_x_limits_enable_checkbox,
                      self.axes_x_limits_from_to_box])
        if figure_options['axes_y_limits'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 100.
        else:
            tmp1 = True
            tmp2 = figure_options['axes_y_limits'][0]
            tmp3 = figure_options['axes_y_limits'][1]
        self.axes_y_limits_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='Y limits')
        self.axes_y_limits_from_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.axes_y_limits_to_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.axes_y_limits_from_to_box = ipywidgets.Box(
            children=[self.axes_y_limits_from_text,
                      self.axes_y_limits_to_text])
        self.axes_y_limits_box = ipywidgets.HBox(
            children=[self.axes_y_limits_enable_checkbox,
                      self.axes_y_limits_from_to_box])
        self.name_size_x_limits = ipywidgets.VBox(
            children=[self.axes_font_name_dropdown, self.axes_font_size_text,
                      self.axes_x_limits_box])
        self.style_weight_y_limits = ipywidgets.VBox(
            children=[self.axes_font_style_dropdown,
                      self.axes_font_weight_dropdown, self.axes_y_limits_box])
        self.name_size_x_limits_style_weight_y_limits = ipywidgets.HBox(
            children=[self.name_size_x_limits,
                      self.style_weight_y_limits])
        super(FigureOptionsOneScaleWidget, self).__init__(
            children=[self.figure_scale_slider, self.render_axes_checkbox,
                      self.name_size_x_limits_style_weight_y_limits])
        self.align = 'start'
        self.figure_scale_slider.slider_width = '8cm'

        # Assign output
        self.selected_values = figure_options

        # Set functionality
        def figure_options_visible(name, value):
            self.axes_font_name_dropdown.disabled = not value
            self.axes_font_size_text.disabled = not value
            self.axes_font_style_dropdown.disabled = not value
            self.axes_font_weight_dropdown.disabled = not value
            self.axes_x_limits_enable_checkbox.disabled = not value
            self.axes_y_limits_enable_checkbox.disabled = not value
            if value:
                self.axes_x_limits_from_text.disabled = \
                    not self.axes_x_limits_enable_checkbox.value
                self.axes_x_limits_to_text.disabled = \
                    not self.axes_x_limits_enable_checkbox.value
                self.axes_y_limits_from_text.disabled = \
                    not self.axes_y_limits_enable_checkbox.value
                self.axes_y_limits_to_text.disabled = \
                    not self.axes_y_limits_enable_checkbox.value
            else:
                self.axes_x_limits_from_text.disabled = True
                self.axes_x_limits_to_text.disabled = True
                self.axes_y_limits_from_text.disabled = True
                self.axes_y_limits_to_text.disabled = True
        figure_options_visible('', figure_options['render_axes'])
        self.render_axes_checkbox.on_trait_change(figure_options_visible,
                                                  'value')

        def save_render_axes(name, value):
            self.selected_values['render_axes'] = value
        self.render_axes_checkbox.on_trait_change(save_render_axes, 'value')

        def save_axes_font_name(name, value):
            self.selected_values['axes_font_name'] = value
        self.axes_font_name_dropdown.on_trait_change(save_axes_font_name,
                                                     'value')

        def save_axes_font_size(name, value):
            self.selected_values['axes_font_size'] = int(value)
        self.axes_font_size_text.on_trait_change(save_axes_font_size, 'value')

        def save_axes_font_style(name, value):
            self.selected_values['axes_font_style'] = value
        self.axes_font_style_dropdown.on_trait_change(save_axes_font_style,
                                                      'value')

        def save_axes_font_weight(name, value):
            self.selected_values['axes_font_weight'] = value
        self.axes_font_weight_dropdown.on_trait_change(save_axes_font_weight,
                                                       'value')

        def axes_x_limits_disable(name, value):
            self.axes_x_limits_from_text.disabled = not value
            self.axes_x_limits_to_text.disabled = not value
        axes_x_limits_disable('', self.axes_x_limits_enable_checkbox.value)
        self.axes_x_limits_enable_checkbox.on_trait_change(
            axes_x_limits_disable, 'value')

        def axes_y_limits_disable(name, value):
            self.axes_y_limits_from_text.disabled = not value
            self.axes_y_limits_to_text.disabled = not value
        axes_y_limits_disable('', self.axes_y_limits_enable_checkbox.value)
        self.axes_y_limits_enable_checkbox.on_trait_change(
            axes_y_limits_disable, 'value')

        def save_axes_x_limits(name, value):
            if self.axes_x_limits_enable_checkbox.value:
                self.selected_values['axes_x_limits'] = \
                    (self.axes_x_limits_from_text.value,
                     self.axes_x_limits_to_text.value)
            else:
                self.selected_values['axes_x_limits'] = None
        self.axes_x_limits_enable_checkbox.on_trait_change(save_axes_x_limits,
                                                           'value')
        self.axes_x_limits_from_text.on_trait_change(save_axes_x_limits,
                                                     'value')
        self.axes_x_limits_to_text.on_trait_change(save_axes_x_limits, 'value')

        def save_axes_y_limits(name, value):
            if self.axes_y_limits_enable_checkbox.value:
                self.selected_values['axes_y_limits'] = \
                    (self.axes_y_limits_from_text.value,
                     self.axes_y_limits_to_text.value)
            else:
                self.selected_values['axes_y_limits'] = None
        self.axes_y_limits_enable_checkbox.on_trait_change(save_axes_y_limits,
                                                           'value')
        self.axes_y_limits_from_text.on_trait_change(save_axes_y_limits,
                                                     'value')
        self.axes_y_limits_to_text.on_trait_change(save_axes_y_limits, 'value')

        def save_scale(name, value):
            self.selected_values['x_scale'] = value
            self.selected_values['y_scale'] = value
        self.figure_scale_slider.on_trait_change(save_scale, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.figure_scale_slider, font_family, font_size,
                    font_style, font_weight)
        format_font(self.render_axes_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.render_axes_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_from_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_to_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_enable_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_from_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_to_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_enable_checkbox, font_family, font_size,
                    font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.figure_scale_slider.on_trait_change(self._render_function,
                                                     'value')
            self.render_axes_checkbox.on_trait_change(self._render_function,
                                                      'value')
            self.axes_font_name_dropdown.on_trait_change(self._render_function,
                                                         'value')
            self.axes_font_size_text.on_trait_change(self._render_function,
                                                     'value')
            self.axes_font_style_dropdown.on_trait_change(self._render_function,
                                                          'value')
            self.axes_font_weight_dropdown.on_trait_change(self._render_function,
                                                           'value')
            self.axes_x_limits_from_text.on_trait_change(self._render_function,
                                                         'value')
            self.axes_x_limits_to_text.on_trait_change(self._render_function,
                                                       'value')
            self.axes_x_limits_enable_checkbox.on_trait_change(
                self._render_function, 'value')
            self.axes_y_limits_from_text.on_trait_change(self._render_function,
                                                         'value')
            self.axes_y_limits_to_text.on_trait_change(self._render_function,
                                                       'value')
            self.axes_y_limits_enable_checkbox.on_trait_change(
                self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.figure_scale_slider.on_trait_change(self._render_function, 'value',
                                                 remove=True)
        self.render_axes_checkbox.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.axes_font_name_dropdown.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_font_size_text.on_trait_change(self._render_function, 'value',
                                                 remove=True)
        self.axes_font_style_dropdown.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.axes_font_weight_dropdown.on_trait_change(self._render_function,
                                                       'value', remove=True)
        self.axes_x_limits_from_text.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_x_limits_to_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_x_limits_enable_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self.axes_y_limits_from_text.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_y_limits_to_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_y_limits_enable_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, figure_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        figure_options : `dict`
            The new set of options. For example ::

                figure_options = {'x_scale': 1.,
                                  'y_scale': 1.,
                                  'render_axes': True,
                                  'axes_font_name': 'serif',
                                  'axes_font_size': 10,
                                  'axes_font_style': 'normal',
                                  'axes_font_weight': 'normal',
                                  'axes_x_limits': None,
                                  'axes_y_limits': None}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.selected_values = figure_options

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update scale slider
        if 'x_scale' in figure_options.keys():
            self.figure_scale_slider.value = figure_options['x_scale']
        elif 'y_scale' in figure_options.keys():
            self.figure_scale_slider.value = figure_options['y_scale']

        # update render axes checkbox
        if 'render_axes' in figure_options.keys():
            self.render_axes_checkbox.value = figure_options['render_axes']

        # update axes_font_name dropdown menu
        if 'axes_font_name' in figure_options.keys():
            self.axes_font_name_dropdown.value = \
                figure_options['axes_font_name']

        # update axes_font_size text box
        if 'axes_font_size' in figure_options.keys():
            self.axes_font_size_text.value = \
                int(figure_options['axes_font_size'])

        # update axes_font_style dropdown menu
        if 'axes_font_style' in figure_options.keys():
            self.axes_font_style_dropdown.value = \
                figure_options['axes_font_style']

        # update axes_font_weight dropdown menu
        if 'axes_font_weight' in figure_options.keys():
            self.axes_font_weight_dropdown.value = \
                figure_options['axes_font_weight']

        # update axes_x_limits
        if 'axes_x_limits' in figure_options.keys():
            if figure_options['axes_x_limits'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 100.
            else:
                tmp1 = True
                tmp2 = figure_options['axes_x_limits'][0]
                tmp3 = figure_options['axes_x_limits'][1]
            self.axes_x_limits_enable_checkbox.value = tmp1
            self.axes_x_limits_from_text.value = tmp2
            self.axes_x_limits_to_text.value = tmp3

        # update axes_y_limits
        if 'axes_y_limits' in figure_options.keys():
            if figure_options['axes_y_limits'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 100.
            else:
                tmp1 = True
                tmp2 = figure_options['axes_y_limits'][0]
                tmp3 = figure_options['axes_y_limits'][1]
            self.axes_y_limits_enable_checkbox.value = tmp1
            self.axes_y_limits_from_text.value = tmp2
            self.axes_y_limits_to_text.value = tmp3

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class FigureOptionsTwoScalesWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting figure related options. Specifically, it
    consists of:

        1) FloatSlider [`self.x_scale_slider`]: scale slider
        2) FloatSlider [`self.y_scale_slider`]: scale slider
        3) Checkbox [`self.coupled_checkbox`]: couples x and y sliders
        4) Box [`self.figure_scale_box`]: box that contains (2), (3), (4)
        5) Checkbox [`self.render_axes_checkbox`]: render axes checkbox
        6) Dropdown [`self.axes_font_name_dropdown`]: sets font family
        7) BoundedFloatText [`self.axes_font_size_text`]: sets font size
        8) Dropdown [`self.axes_font_style_dropdown`]: sets font style
        9) Dropdown [`self.axes_font_weight_dropdown`]: sets font weight
        10) FloatText [`self.axes_x_limits_from_text`]: sets x limit from
        11) FloatText [`self.axes_x_limits_to_text`]: sets x limit to
        12) Checkbox [`self.axes_x_limits_enable_checkbox`]: enables x limit
        13) Box [`self.axes_x_limits_from_to_box`]: box that contains (11), (12)
        14) HBox [`self.axes_x_limits_box`]: box that contains (13), (14)
        15) FloatText [`self.axes_y_limits_from_text`]: sets y limit from
        16) FloatText [`self.axes_y_limits_to_text`]: sets y limit to
        17) Checkbox [`self.axes_y_limits_enable_checkbox`]: enables y limit
        18) Box [`self.axes_y_limits_from_to_box`]: box that contains (15), (16)
        19) HBox [`self.axes_y_limits_box`]: box that contains (17), (18)
        20) Box [`self.options_box`]: box that contains (5), (6), (7), (8), (9),
            (10), (15) and (20)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    figure_options : `dict`
        The initial figure options. Example ::

            figure_options = {'x_scale': 1.,
                              'y_scale': 1.,
                              'render_axes': True,
                              'axes_font_name': 'serif',
                              'axes_font_size': 10,
                              'axes_font_style': 'normal',
                              'axes_font_weight': 'normal',
                              'axes_x_limits': [0, 100],
                              'axes_y_limits': None}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    figure_scale_bounds : (`float`, `float`), optional
        The range of scales that can be optionally applied to the figure.
    figure_scale_step : `float`, optional
        The step of the scale sliders.
    figure_scale_visible : `bool`, optional
        The visibility of the figure scales sliders.
    show_axes_visible : `bool`, optional
        The visibility of the axes checkbox.
    coupled_default : `bool`, optional
        If ``True``, x and y scale sliders are coupled.
    """
    def __init__(self, figure_options, render_function=None,
                 figure_scale_bounds=(0.1, 4.), figure_scale_step=0.05,
                 figure_scale_visible=True, axes_visible=True,
                 coupled_default=False):
        self.x_scale_slider = ipywidgets.FloatSlider(
            description='Figure scale: X', value=figure_options['x_scale'],
            min=figure_scale_bounds[0], max=figure_scale_bounds[1],
            step=figure_scale_step)
        self.y_scale_slider = ipywidgets.FloatSlider(
            description='Y', value=figure_options['y_scale'],
            min=figure_scale_bounds[0], max=figure_scale_bounds[1],
            step=figure_scale_step)
        coupled_default = (coupled_default and
                           (figure_options['x_scale'] ==
                            figure_options['y_scale']))
        self.coupled_checkbox = ipywidgets.Checkbox(description='Coupled',
                                                    value=coupled_default)
        self.xy_link = None
        if coupled_default:
            self.xy_link = link((self.x_scale_slider, 'value'),
                                (self.y_scale_slider, 'value'))
        self.figure_scale_box = ipywidgets.VBox(
            children=[self.x_scale_slider, self.y_scale_slider,
                      self.coupled_checkbox], visible=figure_scale_visible,
            align='end')
        self.render_axes_checkbox = ipywidgets.Checkbox(
            description='Render axes', value=figure_options['render_axes'],
            visible=axes_visible)
        axes_font_name_dict = OrderedDict()
        axes_font_name_dict['serif'] = 'serif'
        axes_font_name_dict['sans-serif'] = 'sans-serif'
        axes_font_name_dict['cursive'] = 'cursive'
        axes_font_name_dict['fantasy'] = 'fantasy'
        axes_font_name_dict['monospace'] = 'monospace'
        self.axes_font_name_dropdown = ipywidgets.Dropdown(
            options=axes_font_name_dict,
            value=figure_options['axes_font_name'], description='Font',
            visible=axes_visible)
        self.axes_font_size_text = ipywidgets.BoundedIntText(
            description='Size', value=figure_options['axes_font_size'],
            min=0, max=10**6, visible=axes_visible)
        axes_font_style_dict = OrderedDict()
        axes_font_style_dict['normal'] = 'normal'
        axes_font_style_dict['italic'] = 'italic'
        axes_font_style_dict['oblique'] = 'oblique'
        self.axes_font_style_dropdown = ipywidgets.Dropdown(
            options=axes_font_style_dict, description='Style',
            value=figure_options['axes_font_style'], visible=axes_visible)
        axes_font_weight_dict = OrderedDict()
        axes_font_weight_dict['normal'] = 'normal'
        axes_font_weight_dict['ultralight'] = 'ultralight'
        axes_font_weight_dict['light'] = 'light'
        axes_font_weight_dict['regular'] = 'regular'
        axes_font_weight_dict['book'] = 'book'
        axes_font_weight_dict['medium'] = 'medium'
        axes_font_weight_dict['roman'] = 'roman'
        axes_font_weight_dict['semibold'] = 'semibold'
        axes_font_weight_dict['demibold'] = 'demibold'
        axes_font_weight_dict['demi'] = 'demi'
        axes_font_weight_dict['bold'] = 'bold'
        axes_font_weight_dict['heavy'] = 'heavy'
        axes_font_weight_dict['extra bold'] = 'extra bold'
        axes_font_weight_dict['black'] = 'black'
        self.axes_font_weight_dropdown = ipywidgets.Dropdown(
            options=axes_font_weight_dict,
            value=figure_options['axes_font_weight'], description='Weight',
            visible=axes_visible)
        if figure_options['axes_x_limits'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 100.
        else:
            tmp1 = True
            tmp2 = figure_options['axes_x_limits'][0]
            tmp3 = figure_options['axes_x_limits'][1]
        self.axes_x_limits_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='X limits')
        self.axes_x_limits_from_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.axes_x_limits_to_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.axes_x_limits_from_to_box = ipywidgets.Box(
            children=[self.axes_x_limits_from_text,
                      self.axes_x_limits_to_text])
        self.axes_x_limits_box = ipywidgets.HBox(
            children=[self.axes_x_limits_enable_checkbox,
                      self.axes_x_limits_from_to_box])
        if figure_options['axes_y_limits'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 100.
        else:
            tmp1 = True
            tmp2 = figure_options['axes_y_limits'][0]
            tmp3 = figure_options['axes_y_limits'][1]
        self.axes_y_limits_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='Y limits')
        self.axes_y_limits_from_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.axes_y_limits_to_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.axes_y_limits_from_to_box = ipywidgets.Box(
            children=[self.axes_y_limits_from_text,
                      self.axes_y_limits_to_text])
        self.axes_y_limits_box = ipywidgets.HBox(
            children=[self.axes_y_limits_enable_checkbox,
                      self.axes_y_limits_from_to_box])
        self.name_size_x_limits = ipywidgets.VBox(
            children=[self.axes_font_name_dropdown, self.axes_font_size_text,
                      self.axes_x_limits_box])
        self.style_weight_y_limits = ipywidgets.VBox(
            children=[self.axes_font_style_dropdown,
                      self.axes_font_weight_dropdown, self.axes_y_limits_box])
        self.name_size_x_limits_style_weight_y_limits = ipywidgets.HBox(
            children=[self.name_size_x_limits,
                      self.style_weight_y_limits])
        super(FigureOptionsTwoScalesWidget, self).__init__(
            children=[self.figure_scale_box, self.render_axes_checkbox,
                      self.name_size_x_limits_style_weight_y_limits])

        self.align = 'start'
        self.x_scale_slider.width = '8cm'
        self.y_scale_slider.width = '8cm'

        # Assign output
        self.selected_values = figure_options

        # Set functionality
        def figure_options_visible(name, value):
            self.axes_font_name_dropdown.disabled = not value
            self.axes_font_size_text.disabled = not value
            self.axes_font_style_dropdown.disabled = not value
            self.axes_font_weight_dropdown.disabled = not value
            self.axes_x_limits_enable_checkbox.disabled = not value
            self.axes_y_limits_enable_checkbox.disabled = not value
            if value:
                self.axes_x_limits_from_text.disabled = \
                    not self.axes_x_limits_enable_checkbox.value
                self.axes_x_limits_to_text.disabled = \
                    not self.axes_x_limits_enable_checkbox.value
                self.axes_y_limits_from_text.disabled = \
                    not self.axes_y_limits_enable_checkbox.value
                self.axes_y_limits_to_text.disabled = \
                    not self.axes_y_limits_enable_checkbox.value
            else:
                self.axes_x_limits_from_text.disabled = True
                self.axes_x_limits_to_text.disabled = True
                self.axes_y_limits_from_text.disabled = True
                self.axes_y_limits_to_text.disabled = True
        figure_options_visible('', figure_options['render_axes'])
        self.render_axes_checkbox.on_trait_change(figure_options_visible,
                                                  'value')

        def save_x_scale(name, value):
            self.selected_values['x_scale'] = self.x_scale_slider.value
        self.x_scale_slider.on_trait_change(save_x_scale, 'value')

        def save_y_scale(name, value):
            self.selected_values['y_scale'] = self.y_scale_slider.value
        self.y_scale_slider.on_trait_change(save_y_scale, 'value')

        # Coupled sliders function
        def coupled_sliders(name, value):
            # If coupled is True, remove self._render_function from y_scale
            # If coupled is False, add self._render_function to y_scale
            if value:
                self.xy_link = link((self.x_scale_slider, 'value'),
                                    (self.y_scale_slider, 'value'))
                self.y_scale_slider.on_trait_change(self._render_function,
                                                    'value', remove=True)
            else:
                self.xy_link.unlink()
                if self._render_function is not None:
                    self.y_scale_slider.on_trait_change(self._render_function,
                                                        'value')
        self.coupled_checkbox.on_trait_change(coupled_sliders, 'value')

        def save_render_axes(name, value):
            self.selected_values['render_axes'] = value
        self.render_axes_checkbox.on_trait_change(save_render_axes, 'value')

        def save_axes_font_name(name, value):
            self.selected_values['axes_font_name'] = value
        self.axes_font_name_dropdown.on_trait_change(save_axes_font_name,
                                                     'value')

        def save_axes_font_size(name, value):
            self.selected_values['axes_font_size'] = int(value)
        self.axes_font_size_text.on_trait_change(save_axes_font_size, 'value')

        def save_axes_font_style(name, value):
            self.selected_values['axes_font_style'] = value
        self.axes_font_style_dropdown.on_trait_change(save_axes_font_style,
                                                      'value')

        def save_axes_font_weight(name, value):
            self.selected_values['axes_font_weight'] = value
        self.axes_font_weight_dropdown.on_trait_change(save_axes_font_weight,
                                                       'value')

        def axes_x_limits_disable(name, value):
            self.axes_x_limits_from_text.disabled = not value
            self.axes_x_limits_to_text.disabled = not value
        axes_x_limits_disable('', self.axes_x_limits_enable_checkbox.value)
        self.axes_x_limits_enable_checkbox.on_trait_change(
            axes_x_limits_disable, 'value')

        def axes_y_limits_disable(name, value):
            self.axes_y_limits_from_text.disabled = not value
            self.axes_y_limits_to_text.disabled = not value
        axes_y_limits_disable('', self.axes_y_limits_enable_checkbox.value)
        self.axes_y_limits_enable_checkbox.on_trait_change(
            axes_y_limits_disable, 'value')

        def save_axes_x_limits(name, value):
            if self.axes_x_limits_enable_checkbox.value:
                self.selected_values['axes_x_limits'] = \
                    (self.axes_x_limits_from_text.value,
                     self.axes_x_limits_to_text.value)
            else:
                self.selected_values['axes_x_limits'] = None
        self.axes_x_limits_enable_checkbox.on_trait_change(save_axes_x_limits,
                                                           'value')
        self.axes_x_limits_from_text.on_trait_change(save_axes_x_limits,
                                                     'value')
        self.axes_x_limits_to_text.on_trait_change(save_axes_x_limits, 'value')

        def save_axes_y_limits(name, value):
            if self.axes_y_limits_enable_checkbox.value:
                self.selected_values['axes_y_limits'] = \
                    (self.axes_y_limits_from_text.value,
                     self.axes_y_limits_to_text.value)
            else:
                self.selected_values['axes_y_limits'] = None
        self.axes_y_limits_enable_checkbox.on_trait_change(save_axes_y_limits,
                                                           'value')
        self.axes_y_limits_from_text.on_trait_change(save_axes_y_limits,
                                                     'value')
        self.axes_y_limits_to_text.on_trait_change(save_axes_y_limits, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.x_scale_slider, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_scale_slider, font_family, font_size, font_style,
                    font_weight)
        format_font(self.coupled_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.render_axes_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.render_axes_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_from_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_to_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_x_limits_enable_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_from_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_to_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.axes_y_limits_enable_checkbox, font_family, font_size,
                    font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.x_scale_slider.on_trait_change(self._render_function, 'value')
            if not self.coupled_checkbox.value:
                self.y_scale_slider.on_trait_change(self._render_function,
                                                    'value')
            self.render_axes_checkbox.on_trait_change(self._render_function,
                                                      'value')
            self.axes_font_name_dropdown.on_trait_change(self._render_function,
                                                         'value')
            self.axes_font_size_text.on_trait_change(self._render_function,
                                                     'value')
            self.axes_font_style_dropdown.on_trait_change(self._render_function,
                                                          'value')
            self.axes_font_weight_dropdown.on_trait_change(self._render_function,
                                                           'value')
            self.axes_x_limits_from_text.on_trait_change(self._render_function,
                                                         'value')
            self.axes_x_limits_to_text.on_trait_change(self._render_function,
                                                       'value')
            self.axes_x_limits_enable_checkbox.on_trait_change(
                self._render_function, 'value')
            self.axes_y_limits_from_text.on_trait_change(self._render_function,
                                                         'value')
            self.axes_y_limits_to_text.on_trait_change(self._render_function,
                                                       'value')
            self.axes_y_limits_enable_checkbox.on_trait_change(
                self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.x_scale_slider.on_trait_change(self._render_function, 'value',
                                            remove=True)
        self.y_scale_slider.on_trait_change(self._render_function, 'value',
                                            remove=True)
        self.render_axes_checkbox.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.axes_font_name_dropdown.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_font_size_text.on_trait_change(self._render_function, 'value',
                                                 remove=True)
        self.axes_font_style_dropdown.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.axes_font_weight_dropdown.on_trait_change(self._render_function,
                                                       'value', remove=True)
        self.axes_x_limits_from_text.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_x_limits_to_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_x_limits_enable_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self.axes_y_limits_from_text.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.axes_y_limits_to_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.axes_y_limits_enable_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, figure_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        figure_options : `dict`
            The new set of options. For example ::

                figure_options = {'x_scale': 1.,
                                  'y_scale': 1.,
                                  'render_axes': True,
                                  'axes_font_name': 'serif',
                                  'axes_font_size': 10,
                                  'axes_font_style': 'normal',
                                  'axes_font_weight': 'normal',
                                  'axes_x_limits': None,
                                  'axes_y_limits': None}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.selected_values = figure_options

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update scale slider
        if ('x_scale' in figure_options.keys() and
                'y_scale' not in figure_options.keys()):
            self.x_scale_slider.value = figure_options['x_scale']
            self.coupled_checkbox.value = False
        elif ('x_scale' not in figure_options.keys() and
                'y_scale' in figure_options.keys()):
            self.y_scale_slider.value = figure_options['y_scale']
            self.coupled_checkbox.value = False
        elif ('x_scale' in figure_options.keys() and
                'y_scale' in figure_options.keys()):
            self.coupled_checkbox.value = (self.coupled_checkbox.value and
                                           (figure_options['x_scale'] ==
                                            figure_options['y_scale']))
            self.x_scale_slider.value = figure_options['x_scale']
            self.y_scale_slider.value = figure_options['y_scale']

        # update render axes checkbox
        if 'render_axes' in figure_options.keys():
            self.render_axes_checkbox.value = figure_options['render_axes']

        # update axes_font_name dropdown menu
        if 'axes_font_name' in figure_options.keys():
            self.axes_font_name_dropdown.value = \
                figure_options['axes_font_name']

        # update axes_font_size text box
        if 'axes_font_size' in figure_options.keys():
            self.axes_font_size_text.value = \
                int(figure_options['axes_font_size'])

        # update axes_font_style dropdown menu
        if 'axes_font_style' in figure_options.keys():
            self.axes_font_style_dropdown.value = \
                figure_options['axes_font_style']

        # update axes_font_weight dropdown menu
        if 'axes_font_weight' in figure_options.keys():
            self.axes_font_weight_dropdown.value = \
                figure_options['axes_font_weight']

        # update axes_x_limits
        if 'axes_x_limits' in figure_options.keys():
            if figure_options['axes_x_limits'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 100.
            else:
                tmp1 = True
                tmp2 = figure_options['axes_x_limits'][0]
                tmp3 = figure_options['axes_x_limits'][1]
            self.axes_x_limits_enable_checkbox.value = tmp1
            self.axes_x_limits_from_text.value = tmp2
            self.axes_x_limits_to_text.value = tmp3

        # update axes_y_limits
        if 'axes_y_limits' in figure_options.keys():
            if figure_options['axes_y_limits'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 100.
            else:
                tmp1 = True
                tmp2 = figure_options['axes_y_limits'][0]
                tmp3 = figure_options['axes_y_limits'][1]
            self.axes_y_limits_enable_checkbox.value = tmp1
            self.axes_y_limits_from_text.value = tmp2
            self.axes_y_limits_to_text.value = tmp3

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class LegendOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting legend rendering options. Specifically, it
    consists of:

        1) Checkbox [`self.render_legend_checkbox`]: render legend checkbox
        2) Dropdown [`self.legend_font_name_dropdown`]: legend font family
        3) BoundedIntText [`self.legend_font_size_text`]: legend font size
        4) Dropdown [`self.legend_font_style_dropdown`]: legend font style
        5) Dropdown [`self.legend_font_weight_dropdown`]: legend font weight
        6) Text [`self.legend_title_text`]: legend title
        7) Box [`self.legend_font_name_and_size_box`]: box containing (2), (3)
        8) Box [`self.legend_font_style_and_weight_box`]: box containing (4), (5)
        9) Box [`self.legend_font_box`]: box containing (7) and (8)
        10) Box [`self.font_related_box`]: box containing (6) and (9)

        11) Dropdown [`self.legend_location_dropdown`]: predefined locations
        12) Checkbox [`self.bbox_to_anchor_enable_checkbox`]: enable bbox to
            anchor
        13) FloatText [`self.bbox_to_anchor_x_text`]: set bbox to anchor x
        14) FloatText [`self.bbox_to_anchor_y_text`]: set bbox to anchor y
        15) Box [`self.legend_bbox_to_anchor_box`]: box containing (12), (13)
            and (14)
        16) BoundedFloatText [`self.legend_border_axes_pad_text`]: border axes
            padding
        17) Box [`self.location_related_box`]: box containing (11), (15), (16)

        18) BoundedIntText [`self.legend_n_columns_text`]: set number of columns
        19) BoundedFloatText [`self.legend_marker_scale_text`]: set marker scale
        20) BoundedFloatText [`self.legend_horizontal_spacing_text`]: set
            horizontal spacing
        21) BoundedFloatText [`self.legend_vertical_spacing_text`]: set vertical
            spacing
        22) Box [`self.legend_n_columns_and_marker_scale_box`]: box containing
            (18) and (19)
        23) Box [`self.legend_horizontal_and_vertical_spacing_box`]: box
            containing (20) and (21)
        24) Box [`self.location_box`]: box containing (22) and (23)
        25) Checkbox [`self.legend_border_checkbox`]: enable border
        26) BoundedFloatText [`self.legend_border_padding_text`]: set border
            padding
        27) Box [`self.border_box`]: box containing (25) and (26)
        28) Checkbox [`self.legend_shadow_checkbox`]: enable shadow
        29) Checkbox [`self.legend_rounded_corners_checkbox`]: enable rounded
            corners
        30) Box [`self.shadow_fancy_box`]: box containing (28) and (29)
        31) Box [`self.formatting_related_box`]: box containing (24), (27), (30)

        32) Tab [`self.tab_box`]: box containing (17), (10) and (31)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    legend_options : `dict`
        The initial legend options. Example ::

            legend_options = {'render_legend': True,
                              'legend_title': '',
                              'legend_font_name': 'serif',
                              'legend_font_style': 'normal',
                              'legend_font_size': 10,
                              'legend_font_weight': 'normal',
                              'legend_marker_scale': 1.,
                              'legend_location': 2,
                              'legend_bbox_to_anchor': (1.05, 1.),
                              'legend_border_axes_pad': 1.,
                              'legend_n_columns': 1,
                              'legend_horizontal_spacing': 1.,
                              'legend_vertical_spacing': 1.,
                              'legend_border': True,
                              'legend_border_padding': 0.5,
                              'legend_shadow': False,
                              'legend_rounded_corners': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render legend checkbox.
    """
    def __init__(self, legend_options, render_function=None,
                 render_checkbox_title='Render legend'):
        # render checkbox
        self.render_legend_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=legend_options['render_legend'])

        # font-related options and title
        legend_font_name_dict = OrderedDict()
        legend_font_name_dict['serif'] = 'serif'
        legend_font_name_dict['sans-serif'] = 'sans-serif'
        legend_font_name_dict['cursive'] = 'cursive'
        legend_font_name_dict['fantasy'] = 'fantasy'
        legend_font_name_dict['monospace'] = 'monospace'
        self.legend_font_name_dropdown = ipywidgets.Dropdown(
            options=legend_font_name_dict,
            value=legend_options['legend_font_name'], description='Font')
        self.legend_font_size_text = ipywidgets.BoundedIntText(
            description='Size', min=0, max=10**6,
            value=legend_options['legend_font_size'])
        legend_font_style_dict = OrderedDict()
        legend_font_style_dict['normal'] = 'normal'
        legend_font_style_dict['italic'] = 'italic'
        legend_font_style_dict['oblique'] = 'oblique'
        self.legend_font_style_dropdown = ipywidgets.Dropdown(
            options=legend_font_style_dict,
            value=legend_options['legend_font_style'], description='Style')
        legend_font_weight_dict = OrderedDict()
        legend_font_weight_dict['normal'] = 'normal'
        legend_font_weight_dict['ultralight'] = 'ultralight'
        legend_font_weight_dict['light'] = 'light'
        legend_font_weight_dict['regular'] = 'regular'
        legend_font_weight_dict['book'] = 'book'
        legend_font_weight_dict['medium'] = 'medium'
        legend_font_weight_dict['roman'] = 'roman'
        legend_font_weight_dict['semibold'] = 'semibold'
        legend_font_weight_dict['demibold'] = 'demibold'
        legend_font_weight_dict['demi'] = 'demi'
        legend_font_weight_dict['bold'] = 'bold'
        legend_font_weight_dict['heavy'] = 'heavy'
        legend_font_weight_dict['extra bold'] = 'extra bold'
        legend_font_weight_dict['black'] = 'black'
        self.legend_font_weight_dropdown = ipywidgets.Dropdown(
            options=legend_font_weight_dict,
            value=legend_options['legend_font_weight'], description='Weight')
        self.legend_title_text = ipywidgets.Text(
            description='Title', value=legend_options['legend_title'],
            width='9cm')
        self.legend_font_name_and_size_box = ipywidgets.HBox(
            children=[self.legend_font_name_dropdown,
                      self.legend_font_size_text])
        self.legend_font_style_and_weight_box = ipywidgets.HBox(
            children=[self.legend_font_style_dropdown,
                      self.legend_font_weight_dropdown])
        self.legend_font_box = ipywidgets.Box(
            children=[self.legend_font_name_and_size_box,
                      self.legend_font_style_and_weight_box])
        self.font_related_box = ipywidgets.Box(
            children=[self.legend_title_text, self.legend_font_box])

        # location-related options
        legend_location_dict = OrderedDict()
        legend_location_dict['best'] = 0
        legend_location_dict['upper right'] = 1
        legend_location_dict['upper left'] = 2
        legend_location_dict['lower left'] = 3
        legend_location_dict['lower right'] = 4
        legend_location_dict['right'] = 5
        legend_location_dict['center left'] = 6
        legend_location_dict['center right'] = 7
        legend_location_dict['lower center'] = 8
        legend_location_dict['upper center'] = 9
        legend_location_dict['center'] = 10
        self.legend_location_dropdown = ipywidgets.Dropdown(
            options=legend_location_dict,
            value=legend_options['legend_location'],
            description='Predefined location')
        if legend_options['legend_bbox_to_anchor'] is None:
            tmp1 = False
            tmp2 = 0.
            tmp3 = 0.
        else:
            tmp1 = True
            tmp2 = legend_options['legend_bbox_to_anchor'][0]
            tmp3 = legend_options['legend_bbox_to_anchor'][1]
        self.bbox_to_anchor_enable_checkbox = ipywidgets.Checkbox(
            value=tmp1, description='Arbitrary location')
        self.bbox_to_anchor_x_text = ipywidgets.FloatText(
            value=tmp2, description='', width='3cm')
        self.bbox_to_anchor_y_text = ipywidgets.FloatText(
            value=tmp3, description='', width='3cm')
        self.legend_bbox_to_anchor_x_y_box = ipywidgets.Box(
            children=[self.bbox_to_anchor_x_text, self.bbox_to_anchor_y_text])
        self.legend_bbox_to_anchor_box = ipywidgets.HBox(
            children=[self.bbox_to_anchor_enable_checkbox,
                      self.legend_bbox_to_anchor_x_y_box])
        self.legend_border_axes_pad_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_border_axes_pad'],
            description='Distance to axes', min=0.)
        self.location_related_box = ipywidgets.VBox(
            children=[self.legend_location_dropdown,
                      self.legend_bbox_to_anchor_box,
                      self.legend_border_axes_pad_text])

        # formatting related
        self.legend_n_columns_text = ipywidgets.BoundedIntText(
            value=legend_options['legend_n_columns'], description='Columns',
            min=0)
        self.legend_marker_scale_text = ipywidgets.BoundedFloatText(
            description='Marker scale',
            value=legend_options['legend_marker_scale'], min=0.)
        self.legend_horizontal_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_horizontal_spacing'],
            description='Horizontal space', min=0.)
        self.legend_vertical_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_vertical_spacing'],
            description='Vertical space', min=0.)
        self.legend_n_columns_and_marker_scale_box = ipywidgets.HBox(
            children=[self.legend_n_columns_text,
                      self.legend_marker_scale_text])
        self.legend_horizontal_and_vertical_spacing_box = ipywidgets.HBox(
            children=[self.legend_horizontal_spacing_text,
                      self.legend_vertical_spacing_text])
        self.location_box = ipywidgets.VBox(
            children=[self.legend_n_columns_and_marker_scale_box,
                      self.legend_horizontal_and_vertical_spacing_box])
        self.legend_border_checkbox = ipywidgets.Checkbox(
            description='Border', value=legend_options['legend_border'])
        self.legend_border_padding_text = ipywidgets.BoundedFloatText(
            value=legend_options['legend_border_padding'],
            description='Border pad', min=0.)
        self.border_box = ipywidgets.HBox(
            children=[self.legend_border_checkbox,
                      self.legend_border_padding_text])
        self.legend_shadow_checkbox = ipywidgets.Checkbox(
            description='Shadow', value=legend_options['legend_shadow'])
        self.legend_rounded_corners_checkbox = ipywidgets.Checkbox(
            description='Rounded corners',
            value=legend_options['legend_rounded_corners'])
        self.shadow_fancy_box = ipywidgets.Box(
            children=[self.legend_shadow_checkbox,
                      self.legend_rounded_corners_checkbox])
        self.formatting_related_box = ipywidgets.Box(
            children=[self.location_box, self.border_box,
                      self.shadow_fancy_box])

        # Options widget
        self.tab_box = ipywidgets.Tab(
            children=[self.location_related_box, self.font_related_box,
                      self.formatting_related_box])
        self.options_box = ipywidgets.VBox(
            children=[self.render_legend_checkbox, self.tab_box], align='end')
        super(LegendOptionsWidget, self).__init__(children=[self.options_box])
        self.align = 'start'

        # Set tab titles
        tab_titles = ['Location', 'Font', 'Formatting']
        for (k, tl) in enumerate(tab_titles):
            self.tab_box.set_title(k, tl)

        # Assign output
        self.selected_values = legend_options

        # Set functionality
        def legend_options_visible(name, value):
            self.legend_title_text.disabled = not value
            self.legend_font_name_dropdown.disabled = not value
            self.legend_font_size_text.disabled = not value
            self.legend_font_style_dropdown.disabled = not value
            self.legend_font_weight_dropdown.disabled = not value
            self.legend_location_dropdown.disabled = not value
            self.bbox_to_anchor_enable_checkbox.disabled = not value
            self.bbox_to_anchor_x_text.disabled = not value or not self.bbox_to_anchor_enable_checkbox.value
            self.bbox_to_anchor_y_text.disabled = not value or not self.bbox_to_anchor_enable_checkbox.value
            self.legend_border_axes_pad_text.disabled = not value
            self.legend_n_columns_text.disabled = not value
            self.legend_marker_scale_text.disabled = not value
            self.legend_horizontal_spacing_text.disabled = not value
            self.legend_vertical_spacing_text.disabled = not value
            self.legend_border_checkbox.disabled = not value
            self.legend_border_padding_text.disabled = not value or not self.legend_border_checkbox.value
            self.legend_shadow_checkbox.disabled = not value
            self.legend_rounded_corners_checkbox.disabled = not value
        legend_options_visible('', legend_options['render_legend'])
        self.render_legend_checkbox.on_trait_change(legend_options_visible,
                                                    'value')

        def border_pad_visible(name, value):
            self.legend_border_padding_text.visible = value
        self.legend_border_checkbox.on_trait_change(border_pad_visible, 'value')

        def bbox_to_anchor_disable(name, value):
            self.bbox_to_anchor_x_text.disabled = not value
            self.bbox_to_anchor_y_text.disabled = not value
        self.bbox_to_anchor_enable_checkbox.on_trait_change(
            bbox_to_anchor_disable, 'value')

        def save_show_legend(name, value):
            self.selected_values['render_legend'] = value
        self.render_legend_checkbox.on_trait_change(save_show_legend, 'value')

        def save_title(name, value):
            self.selected_values['legend_title'] = str(value)
        self.legend_title_text.on_trait_change(save_title, 'value')

        def save_fontname(name, value):
            self.selected_values['legend_font_name'] = value
        self.legend_font_name_dropdown.on_trait_change(save_fontname, 'value')

        def save_fontsize(name, value):
            self.selected_values['legend_font_size'] = int(value)
        self.legend_font_size_text.on_trait_change(save_fontsize, 'value')

        def save_fontstyle(name, value):
            self.selected_values['legend_font_style'] = value
        self.legend_font_style_dropdown.on_trait_change(save_fontstyle, 'value')

        def save_fontweight(name, value):
            self.selected_values['legend_font_weight'] = value
        self.legend_font_weight_dropdown.on_trait_change(save_fontweight,
                                                         'value')

        def save_location(name, value):
            self.selected_values['legend_location'] = value
        self.legend_location_dropdown.on_trait_change(save_location, 'value')

        def save_bbox_to_anchor(name, value):
            if self.bbox_to_anchor_enable_checkbox.value:
                self.selected_values['legend_bbox_to_anchor'] = \
                    (self.bbox_to_anchor_x_text.value,
                     self.bbox_to_anchor_y_text.value)
            else:
                self.selected_values['legend_bbox_to_anchor'] = None
        self.bbox_to_anchor_enable_checkbox.on_trait_change(save_bbox_to_anchor,
                                                            'value')
        self.bbox_to_anchor_x_text.on_trait_change(save_bbox_to_anchor, 'value')
        self.bbox_to_anchor_y_text.on_trait_change(save_bbox_to_anchor, 'value')

        def save_borderaxespad(name, value):
            self.selected_values['legend_border_axes_pad'] = float(value)
        self.legend_border_axes_pad_text.on_trait_change(save_borderaxespad,
                                                         'value')

        def save_n_columns(name, value):
            self.selected_values['legend_n_columns'] = int(value)
        self.legend_n_columns_text.on_trait_change(save_n_columns, 'value')

        def save_markerscale(name, value):
            self.selected_values['legend_marker_scale'] = float(value)
        self.legend_marker_scale_text.on_trait_change(save_markerscale, 'value')

        def save_horizontal_spacing(name, value):
            self.selected_values['legend_horizontal_spacing'] = float(value)
        self.legend_horizontal_spacing_text.on_trait_change(
            save_horizontal_spacing, 'value')

        def save_vertical_spacing(name, value):
            self.selected_values['legend_vertical_spacing'] = float(value)
        self.legend_vertical_spacing_text.on_trait_change(save_vertical_spacing,
                                                          'value')

        def save_draw_border(name, value):
            self.selected_values['legend_border'] = value
        self.legend_border_checkbox.on_trait_change(save_draw_border, 'value')

        def save_border_padding(name, value):
            self.selected_values['legend_border_padding'] = float(value)
        self.legend_border_padding_text.on_trait_change(save_border_padding,
                                                        'value')

        def save_draw_shadow(name, value):
            self.selected_values['legend_shadow'] = value
        self.legend_shadow_checkbox.on_trait_change(save_draw_shadow, 'value')

        def save_fancy_corners(name, value):
            self.selected_values['legend_rounded_corners'] = value
        self.legend_rounded_corners_checkbox.on_trait_change(save_fancy_corners,
                                                             'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_legend_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_name_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_font_weight_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_title_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.legend_location_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.bbox_to_anchor_enable_checkbox, font_family,
                    font_size, font_style, font_weight)
        format_font(self.bbox_to_anchor_x_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.bbox_to_anchor_y_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_axes_pad_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_n_columns_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_marker_scale_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_horizontal_spacing_text, font_family,
                    font_size, font_style, font_weight)
        format_font(self.legend_vertical_spacing_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_border_padding_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_shadow_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.legend_rounded_corners_checkbox, font_family,
                    font_size, font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.render_legend_checkbox.on_trait_change(self._render_function,
                                                        'value')
            self.legend_title_text.on_trait_change(self._render_function,
                                                   'value')
            self.legend_font_name_dropdown.on_trait_change(
                self._render_function, 'value')
            self.legend_font_style_dropdown.on_trait_change(
                self._render_function, 'value')
            self.legend_font_size_text.on_trait_change(self._render_function,
                                                       'value')
            self.legend_font_weight_dropdown.on_trait_change(
                self._render_function, 'value')
            self.legend_location_dropdown.on_trait_change(self._render_function,
                                                          'value')
            self.bbox_to_anchor_enable_checkbox.on_trait_change(
                self._render_function, 'value')
            self.bbox_to_anchor_x_text.on_trait_change(self._render_function,
                                                       'value')
            self.bbox_to_anchor_y_text.on_trait_change(self._render_function,
                                                       'value')
            self.legend_border_axes_pad_text.on_trait_change(
                self._render_function, 'value')
            self.legend_n_columns_text.on_trait_change(self._render_function,
                                                       'value')
            self.legend_marker_scale_text.on_trait_change(self._render_function,
                                                          'value')
            self.legend_horizontal_spacing_text.on_trait_change(
                self._render_function, 'value')
            self.legend_vertical_spacing_text.on_trait_change(
                self._render_function, 'value')
            self.legend_border_checkbox.on_trait_change(self._render_function,
                                                        'value')
            self.legend_border_padding_text.on_trait_change(
                self._render_function, 'value')
            self.legend_shadow_checkbox.on_trait_change(self._render_function,
                                                        'value')
            self.legend_rounded_corners_checkbox.on_trait_change(
                self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.render_legend_checkbox.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.legend_title_text.on_trait_change(self._render_function, 'value',
                                               remove=True)
        self.legend_font_name_dropdown.on_trait_change(self._render_function,
                                                       'value', remove=True)
        self.legend_font_style_dropdown.on_trait_change(self._render_function,
                                                        'value', remove=True)
        self.legend_font_size_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.legend_font_weight_dropdown.on_trait_change(self._render_function,
                                                         'value', remove=True)
        self.legend_location_dropdown.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.bbox_to_anchor_enable_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self.bbox_to_anchor_x_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.bbox_to_anchor_y_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.legend_border_axes_pad_text.on_trait_change(self._render_function,
                                                         'value', remove=True)
        self.legend_n_columns_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.legend_marker_scale_text.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.legend_horizontal_spacing_text.on_trait_change(
            self._render_function, 'value', remove=True)
        self.legend_vertical_spacing_text.on_trait_change(self._render_function,
                                                          'value', remove=True)
        self.legend_border_checkbox.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.legend_border_padding_text.on_trait_change(self._render_function,
                                                        'value', remove=True)
        self.legend_shadow_checkbox.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.legend_rounded_corners_checkbox.on_trait_change(
            self._render_function, 'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, legend_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        legend_options : `dict`
            The new set of options. For example ::

                legend_options = {'render_legend': True,
                                  'legend_title': '',
                                  'legend_font_name': 'serif',
                                  'legend_font_style': 'normal',
                                  'legend_font_size': 10,
                                  'legend_font_weight': 'normal',
                                  'legend_marker_scale': 1.,
                                  'legend_location': 2,
                                  'legend_bbox_to_anchor': (1.05, 1.),
                                  'legend_border_axes_pad': 1.,
                                  'legend_n_columns': 1,
                                  'legend_horizontal_spacing': 1.,
                                  'legend_vertical_spacing': 1.,
                                  'legend_border': True,
                                  'legend_border_padding': 0.5,
                                  'legend_shadow': False,
                                  'legend_rounded_corners': True}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.selected_values = legend_options

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update render legend checkbox
        if 'render_legend' in legend_options.keys():
            self.render_legend_checkbox.value = legend_options['render_legend']

        # update legend_title
        if 'legend_title' in legend_options.keys():
            self.legend_title_text.value = legend_options['legend_title']

        # update legend_font_name dropdown menu
        if 'legend_font_name' in legend_options.keys():
            self.legend_font_name_dropdown.value = \
                legend_options['legend_font_name']

        # update legend_font_size text box
        if 'legend_font_size' in legend_options.keys():
            self.legend_font_size_text.value = \
                int(legend_options['legend_font_size'])

        # update legend_font_style dropdown menu
        if 'legend_font_style' in legend_options.keys():
            self.legend_font_style_dropdown.value = \
                legend_options['legend_font_style']

        # update legend_font_weight dropdown menu
        if 'legend_font_weight' in legend_options.keys():
            self.legend_font_weight_dropdown.value = \
                legend_options['legend_font_weight']

        # update legend_location dropdown menu
        if 'legend_location' in legend_options.keys():
            self.legend_location_dropdown.value = \
                legend_options['legend_location']

        # update legend_bbox_to_anchor
        if 'legend_bbox_to_anchor' in legend_options.keys():
            if legend_options['legend_bbox_to_anchor'] is None:
                tmp1 = False
                tmp2 = 0.
                tmp3 = 0.
            else:
                tmp1 = True
                tmp2 = legend_options['legend_bbox_to_anchor'][0]
                tmp3 = legend_options['legend_bbox_to_anchor'][1]
            self.bbox_to_anchor_enable_checkbox.value = tmp1
            self.bbox_to_anchor_x_text.value = tmp2
            self.bbox_to_anchor_y_text.value = tmp3

        # update legend_border_axes_pad
        if 'legend_border_axes_pad' in legend_options.keys():
            self.legend_border_axes_pad_text.value = \
                legend_options['legend_border_axes_pad']

        # update legend_n_columns text box
        if 'legend_n_columns' in legend_options.keys():
            self.legend_n_columns_text.value = \
                int(legend_options['legend_n_columns'])

        # update legend_marker_scale text box
        if 'legend_marker_scale' in legend_options.keys():
            self.legend_marker_scale_text.value = \
                float(legend_options['legend_marker_scale'])

        # update legend_horizontal_spacing text box
        if 'legend_horizontal_spacing' in legend_options.keys():
            self.legend_horizontal_spacing_text.value = \
                float(legend_options['legend_horizontal_spacing'])

        # update legend_vertical_spacing text box
        if 'legend_vertical_spacing' in legend_options.keys():
            self.legend_vertical_spacing_text.value = \
                float(legend_options['legend_vertical_spacing'])

        # update legend_border
        if 'legend_border' in legend_options.keys():
            self.legend_border_checkbox.value = \
                legend_options['legend_border']

        # update legend_border_padding text box
        if 'legend_border_padding' in legend_options.keys():
            self.legend_border_padding_text.value = \
                float(legend_options['legend_border_padding'])

        # update legend_shadow
        if 'legend_shadow' in legend_options.keys():
            self.legend_shadow_checkbox.value = legend_options['legend_shadow']

        # update legend_rounded_corners
        if 'legend_rounded_corners' in legend_options.keys():
            self.legend_rounded_corners_checkbox.value = \
                legend_options['legend_rounded_corners']

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class GridOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting grid rendering options. Specifically, it
    consists of:

        1) Checkbox [`self.render_grid_checkbox`]: whether to render the grid
        2) BoundedFloatText [`self.grid_line_width_text`]: sets the line width
        3) Dropdown [`self.grid_line_style_dropdown`]: sets the line style
        4) Box [`self.grid_options_box`]: box that contains (2) and (3)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    grid_options : `dict`
        The initial grid options. Example ::

            grid_options = {'render_grid': True,
                            'grid_line_width': 1,
                            'grid_line_style': '-'}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    """
    def __init__(self, grid_options, render_function=None,
                 render_checkbox_title='Render grid'):
        self.render_grid_checkbox = ipywidgets.Checkbox(
            description=render_checkbox_title,
            value=grid_options['render_grid'])
        self.grid_line_width_text = ipywidgets.BoundedFloatText(
            description='Width', value=grid_options['grid_line_width'],
            min=0., max=10**6)
        grid_line_style_dict = OrderedDict()
        grid_line_style_dict['solid'] = '-'
        grid_line_style_dict['dashed'] = '--'
        grid_line_style_dict['dash-dot'] = '-.'
        grid_line_style_dict['dotted'] = ':'
        self.grid_line_style_dropdown = ipywidgets.Dropdown(
            value=grid_options['grid_line_style'], description='Style',
            options=grid_line_style_dict,)

        # Options widget
        self.grid_options_box = ipywidgets.Box(
            children=[self.grid_line_style_dropdown, self.grid_line_width_text])
        self.options_box = ipywidgets.VBox(
            children=[self.render_grid_checkbox, self.grid_options_box],
            align='end')
        super(GridOptionsWidget, self).__init__(children=[self.options_box])
        self.align = 'start'

        # Assign output
        self.selected_values = grid_options

        # Set functionality
        def grid_options_visible(name, value):
            self.grid_line_style_dropdown.disabled = not value
            self.grid_line_width_text.disabled = not value
        grid_options_visible('', grid_options['render_grid'])
        self.render_grid_checkbox.on_trait_change(grid_options_visible, 'value')

        def save_render_grid(name, value):
            self.selected_values['render_grid'] = value
        self.render_grid_checkbox.on_trait_change(save_render_grid, 'value')

        def save_grid_line_width(name, value):
            self.selected_values['grid_line_width'] = float(value)
        self.grid_line_width_text.on_trait_change(save_grid_line_width, 'value')

        def save_grid_line_style(name, value):
            self.selected_values['grid_line_style'] = value
        self.grid_line_style_dropdown.on_trait_change(save_grid_line_style,
                                                      'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_grid_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.grid_line_style_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.grid_line_width_text, font_family, font_size,
                    font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.render_grid_checkbox.on_trait_change(self._render_function,
                                                      'value')
            self.grid_line_style_dropdown.on_trait_change(self._render_function,
                                                          'value')
            self.grid_line_width_text.on_trait_change(self._render_function,
                                                      'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.render_grid_checkbox.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.grid_line_style_dropdown.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.grid_line_width_text.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def set_widget_state(self, grid_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        grid_options : `dict`
            The new set of options. For example ::

                grid_options = {'render_grid': True,
                                'grid_line_width': 2,
                                'grid_line_style': '-'}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.selected_values = grid_options

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update render grid checkbox
        if 'render_grid' in grid_options.keys():
            self.render_grid_checkbox.value = grid_options['render_grid']

        # update grid_line_style dropdown menu
        if 'grid_line_style' in grid_options.keys():
            self.grid_line_style_dropdown.value = \
                grid_options['grid_line_style']

        # update grid_line_width text box
        if 'grid_line_width' in grid_options.keys():
            self.grid_line_width_text.value = \
                float(grid_options['grid_line_width'])

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class HOGOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting HOG options. Specifically, it consists of:

        1) Radiobuttons [`self.mode_radiobuttons`]: 'dense' or 'sparse' mode
        2) Checkbox [`self.padding_checkbox`]: controls padding of output image
        3) HBox [`self.mode_padding_box`]: box that contains (1) and (2)
        4) BoundedIntText [`self.window_height_text`]: sets window height
        5) BoundedIntText [`self.window_width_text`]: sets window width
        6) RadioButtons [`self.window_size_unit_radiobuttons`]: window size unit
        7) VBox [`self.window_size_box`]: box that contains (4), (5) and (6)
        8) BoundedIntText [`self.window_vertical_text`]: window step Y
        9) BoundedIntText [`self.window_horizontal_text`]: window step X
        10) RadioButtons [`self.window_step_unit_radiobuttons`]: window step
            unit
        11) VBox [`self.window_step_box`]: box that contains (8), (9) and (10)
        12) HBox [`self.window_size_step_box`]: box that contains (7) and (11)
        13) Box [`self.window_box`]: box that contains (3) and (12)
        14) RadioButtons [`self.algorithm_radiobuttons`]: `zhuramanan` or
            `dalaltriggs`
        15) BoundedIntText [`self.cell_size_text`]: cell size in pixels
        16) BoundedIntText [`self.block_size_text`]: block size in pixels
        17) BoundedIntText [`self.num_bins_text`]: number of orientation bins
        18) VBox [`self.algorithm_sizes_box`]: box that contains (15), (16) and
            (17)
        19) Checkbox (`self.signed_gradient_checkbox`]: signed or unsigned
            gradients
        20) BoundedFloatText [`self.l2_norm_clipping_text`]: l2 norm clipping
        21) Box [`self.algorithm_other_box`]: box that contains (19) and (20)
        22) HBox [`self.algorithm_options_box`]: box containing (18) and (21)
        23) Box [`self.algorithm_box`]: box that contains (14) and (22)
        24) Tab [`self.options_box`]: box that contains (13) and (23)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    hog_options : `dict`
        The initial options. Example ::

            hog_options = {'mode': 'dense',
                           'algorithm': 'dalaltriggs',
                           'num_bins': 9,
                           'cell_size': 8,
                           'block_size': 2,
                           'signed_gradient': True,
                           'l2_norm_clip': 0.2,
                           'window_height': 1,
                           'window_width': 1,
                           'window_unit': 'blocks',
                           'window_step_vertical': 1,
                           'window_step_horizontal': 1,
                           'window_step_unit': 'pixels',
                           'padding': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, hog_options, render_function=None):
        # Window related options
        tmp = OrderedDict()
        tmp['Dense'] = 'dense'
        tmp['Sparse'] = 'sparse'
        self.mode_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Mode', value=hog_options['mode'])
        self.padding_checkbox = ipywidgets.Checkbox(
            description='Padding', value=hog_options['padding'])
        self.mode_padding_box = ipywidgets.HBox(
            children=[self.mode_radiobuttons, self.padding_checkbox])
        self.window_height_text = ipywidgets.BoundedIntText(
            value=hog_options['window_height'], description='Height',
            min=1, width='2cm')
        self.window_width_text = ipywidgets.BoundedIntText(
            value=hog_options['window_width'], description='Width',
            min=1, width='2cm')
        tmp = OrderedDict()
        tmp['Blocks'] = 'blocks'
        tmp['Pixels'] = 'pixels'
        self.window_size_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description=' Size unit',
            value=hog_options['window_unit'])
        self.window_size_box = ipywidgets.VBox(
            children=[self.window_height_text, self.window_width_text,
                      self.window_size_unit_radiobuttons])
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=hog_options['window_step_vertical'],
            description='Step Y', min=1, width='2cm')
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=hog_options['window_step_horizontal'],
            description='Step X', min=1, width='2cm')
        tmp = OrderedDict()
        tmp['Pixels'] = 'pixels'
        tmp['Cells'] = 'cells'
        self.window_step_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Step unit',
            value=hog_options['window_step_unit'])
        self.window_step_box = ipywidgets.VBox(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.window_step_unit_radiobuttons])
        self.window_size_step_box = ipywidgets.HBox(
            children=[self.window_size_box, self.window_step_box])
        self.window_box = ipywidgets.Box(children=[self.mode_padding_box,
                                                   self.window_size_step_box])

        # Algorithm related options
        tmp = OrderedDict()
        tmp['Dalal & Triggs'] = 'dalaltriggs'
        tmp['Zhu & Ramanan'] = 'zhuramanan'
        self.algorithm_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, value=hog_options['algorithm'],
            description='Algorithm')
        self.cell_size_text = ipywidgets.BoundedIntText(
            value=hog_options['cell_size'],
            description='Cell size (in pixels)', min=1, width='2cm')
        self.block_size_text = ipywidgets.BoundedIntText(
            value=hog_options['block_size'],
            description='Block size (in cells)', min=1, width='2cm')
        self.num_bins_text = ipywidgets.BoundedIntText(
            value=hog_options['num_bins'],
            description='Orientation bins', min=1, width='2cm')
        self.algorithm_sizes_box = ipywidgets.VBox(
            children=[self.cell_size_text, self.block_size_text,
                      self.num_bins_text])
        self.signed_gradient_checkbox = ipywidgets.Checkbox(
            value=hog_options['signed_gradient'],
            description='Signed gradients')
        self.l2_norm_clipping_text = ipywidgets.BoundedFloatText(
            value=hog_options['l2_norm_clip'],
            description='L2 norm clipping', min=0., width='2cm')
        self.algorithm_other_box = ipywidgets.Box(
            children=[self.signed_gradient_checkbox,
                      self.l2_norm_clipping_text])
        self.algorithm_options_box = ipywidgets.HBox(
            children=[self.algorithm_sizes_box, self.algorithm_other_box])
        self.algorithm_box = ipywidgets.Box(
            children=[self.algorithm_radiobuttons, self.algorithm_options_box])

        # Final widget
        self.options_box = ipywidgets.Tab(children=[self.window_box,
                                                    self.algorithm_box])
        super(HOGOptionsWidget, self).__init__(children=[self.options_box])

        # set tab titles
        tab_titles = ['Window', 'Algorithm']
        for (k, tl) in enumerate(tab_titles):
            self.options_box.set_title(k, tl)

        # Assign output
        self.selected_values = hog_options

        # Set functionality
        def window_mode(name, value):
            self.window_horizontal_text.disabled = value == 'sparse'
            self.window_vertical_text.disabled = value == 'sparse'
            self.window_step_unit_radiobuttons.disabled = value == 'sparse'
            self.window_height_text.disabled = value == 'sparse'
            self.window_width_text.disabled = value == 'sparse'
            self.window_size_unit_radiobuttons.disabled = value == 'sparse'
        self.mode_radiobuttons.on_trait_change(window_mode, 'value')

        # algorithm function
        def algorithm_mode(name, value):
            self.l2_norm_clipping_text.disabled = value == 'zhuramanan'
            self.signed_gradient_checkbox.disabled = value == 'zhuramanan'
            self.block_size_text.disabled = value == 'zhuramanan'
            self.num_bins_text.disabled = value == 'zhuramanan'
        self.algorithm_radiobuttons.on_trait_change(algorithm_mode, 'value')

        # get options
        def get_mode(name, value):
            self.selected_values['mode'] = value
        self.mode_radiobuttons.on_trait_change(get_mode, 'value')

        def get_padding(name, value):
            self.selected_values['padding'] = value
        self.padding_checkbox.on_trait_change(get_padding, 'value')

        def get_window_height(name, value):
            self.selected_values['window_height'] = value
        self.window_height_text.on_trait_change(get_window_height, 'value')

        def get_window_width(name, value):
            self.selected_values['window_width'] = value
        self.window_width_text.on_trait_change(get_window_width, 'value')

        def get_window_size_unit(name, value):
            self.selected_values['window_unit'] = value
        self.window_size_unit_radiobuttons.on_trait_change(get_window_size_unit,
                                                           'value')

        def get_window_step_vertical(name, value):
            self.selected_values['window_step_vertical'] = value
        self.window_vertical_text.on_trait_change(get_window_step_vertical,
                                                  'value')

        def get_window_step_horizontal(name, value):
            self.selected_values['window_step_horizontal'] = value
        self.window_horizontal_text.on_trait_change(get_window_step_horizontal,
                                                    'value')

        def get_window_step_unit(name, value):
            self.selected_values['window_step_unit'] = value
        self.window_step_unit_radiobuttons.on_trait_change(get_window_step_unit,
                                                           'value')

        def get_algorithm(name, value):
            self.selected_values['algorithm'] = value
        self.algorithm_radiobuttons.on_trait_change(get_algorithm, 'value')

        def get_num_bins(name, value):
            self.selected_values['num_bins'] = value
        self.num_bins_text.on_trait_change(get_num_bins, 'value')

        def get_cell_size(name, value):
            self.selected_values['cell_size'] = value
        self.cell_size_text.on_trait_change(get_cell_size, 'value')

        def get_block_size(name, value):
            self.selected_values['block_size'] = value
        self.block_size_text.on_trait_change(get_block_size, 'value')

        def get_signed_gradient(name, value):
            self.selected_values['signed_gradient'] = value
        self.signed_gradient_checkbox.on_trait_change(get_signed_gradient,
                                                      'value')

        def get_l2_norm_clip(name, value):
            self.selected_values['l2_norm_clip'] = value
        self.l2_norm_clipping_text.on_trait_change(get_l2_norm_clip, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.options_box, font_family, font_size, font_style,
                    font_weight)
        format_font(self.mode_radiobuttons, font_family, font_size, font_style,
                    font_weight)
        format_font(self.padding_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_height_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_width_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_size_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_step_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.algorithm_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cell_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.block_size_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.num_bins_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.signed_gradient_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.l2_norm_clipping_text, font_family, font_size,
                    font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.mode_radiobuttons.on_trait_change(self._render_function,
                                                   'value')
            self.padding_checkbox.on_trait_change(self._render_function,
                                                  'value')
            self.window_height_text.on_trait_change(self._render_function,
                                                    'value')
            self.window_width_text.on_trait_change(self._render_function,
                                                   'value')
            self.window_size_unit_radiobuttons.on_trait_change(
                self._render_function, 'value')
            self.window_vertical_text.on_trait_change(self._render_function,
                                                      'value')
            self.window_horizontal_text.on_trait_change(self._render_function,
                                                        'value')
            self.window_step_unit_radiobuttons.on_trait_change(
                self._render_function, 'value')
            self.algorithm_radiobuttons.on_trait_change(self._render_function,
                                                        'value')
            self.cell_size_text.on_trait_change(self._render_function, 'value')
            self.block_size_text.on_trait_change(self._render_function, 'value')
            self.num_bins_text.on_trait_change(self._render_function, 'value')
            self.signed_gradient_checkbox.on_trait_change(self._render_function,
                                                          'value')
            self.l2_norm_clipping_text.on_trait_change(self._render_function,
                                                       'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.mode_radiobuttons.on_trait_change(self._render_function, 'value',
                                               remove=True)
        self.padding_checkbox.on_trait_change(self._render_function, 'value',
                                              remove=True)
        self.window_height_text.on_trait_change(self._render_function, 'value',
                                                remove=True)
        self.window_width_text.on_trait_change(self._render_function, 'value',
                                               remove=True)
        self.window_size_unit_radiobuttons.on_trait_change(
            self._render_function, 'value', remove=True)
        self.window_vertical_text.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.window_horizontal_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.window_step_unit_radiobuttons.on_trait_change(self._render_function,
                                                           'value', remove=True)
        self.algorithm_radiobuttons.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.cell_size_text.on_trait_change(self._render_function, 'value',
                                            remove=True)
        self.block_size_text.on_trait_change(self._render_function, 'value',
                                             remove=True)
        self.num_bins_text.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self.signed_gradient_checkbox.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.l2_norm_clipping_text.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)


class DSIFTOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting desnse SIFT options. Specifically, it
    consists of:

        1) BoundedIntText [`self.window_vertical_text`]: window step Y
        2) BoundedIntText [`self.window_horizontal_text`]: window step X
        3) Checkbox (`self.fast_checkbox`]: fast computation
        4) VBox [`self.window_step_box']: box that contains (1), (2) and (3)
        5) BoundedIntText [`self.cell_size_vertical_text`]: cell size Y
        6) BoundedIntText [`self.cell_size_horizontal_text`]: cell size X
        7) VBox [`self.cell_size_box']: box that contains (5) and (6)
        8) BoundedIntText [`self.num_bins_vertical_text`]: num bins Y
        9) BoundedIntText [`self.num_bins_horizontal_text`]: num bins X
        10) BoundedIntText [`self.num_or_bins_text`]: orientation bins
        11) VBox [`self.cell_size_box']: box that contains (9), (0) and (10)
        12) Tab [`self.options_box`]: box that contains (4), (7) and (11)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    dsift_options : `dict`
        The initial options. Example ::

            dsift_options = {'window_step_horizontal': 1,
                             'window_step_vertical': 1,
                             'num_bins_horizontal': 2,
                             'num_bins_vertical': 2,
                             'num_or_bins': 9,
                             'cell_size_horizontal': 6,
                             'cell_size_vertical': 6,
                             'fast': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, dsift_options, render_function=None):
        # Create widgets
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['window_step_vertical'],
            description='Step Y', min=1, width='2cm')
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['window_step_horizontal'],
            description='Step X', min=1, width='2cm')
        self.fast_checkbox = ipywidgets.Checkbox(
            value=dsift_options['fast'],
            description='Fast computation')
        self.cell_size_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['cell_size_vertical'],
            description='Cell size Y', min=1, width='2cm')
        self.cell_size_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['cell_size_horizontal'],
            description='Cell size X', min=1, width='2cm')
        self.num_bins_vertical_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_bins_vertical'],
            description='Bins Y', min=1, width='2cm')
        self.num_bins_horizontal_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_bins_horizontal'],
            description='Bins X', min=1, width='2cm')
        self.num_or_bins_text = ipywidgets.BoundedIntText(
            value=dsift_options['num_or_bins'],
            description='Orientation bins', min=1, width='2cm')

        # Final widget
        self.window_step_box = ipywidgets.VBox(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.fast_checkbox])
        self.cell_size_box = ipywidgets.VBox(
            children=[self.cell_size_vertical_text,
                      self.cell_size_horizontal_text])
        self.num_bins_box = ipywidgets.VBox(
            children=[self.num_bins_vertical_text,
                      self.num_bins_horizontal_text, self.num_or_bins_text])
        self.options_box = ipywidgets.HBox(children=[self.window_step_box,
                                                     self.cell_size_box,
                                                     self.num_bins_box])
        super(DSIFTOptionsWidget, self).__init__(children=[self.options_box])

        # Assign output
        self.selected_values = dsift_options

        # Get options
        def get_window_step_vertical(name, value):
            self.selected_values['window_step_vertical'] = value
        self.window_vertical_text.on_trait_change(get_window_step_vertical,
                                                  'value')

        def get_window_step_horizontal(name, value):
            self.selected_values['window_step_horizontal'] = value
        self.window_horizontal_text.on_trait_change(get_window_step_horizontal,
                                                    'value')

        def get_num_bins_vertical(name, value):
            self.selected_values['num_bins_vertical'] = value
        self.num_bins_vertical_text.on_trait_change(get_num_bins_vertical,
                                                    'value')

        def get_num_bins_horizontal(name, value):
            self.selected_values['num_bins_horizontal'] = value
        self.num_bins_horizontal_text.on_trait_change(get_num_bins_horizontal,
                                                      'value')

        def get_num_or_bins(name, value):
            self.selected_values['num_or_bins'] = value
        self.num_or_bins_text.on_trait_change(get_num_or_bins, 'value')

        def get_cell_size_vertical(name, value):
            self.selected_values['cell_size_vertical'] = value
        self.cell_size_vertical_text.on_trait_change(get_cell_size_vertical,
                                                     'value')

        def get_cell_size_horizontal(name, value):
            self.selected_values['cell_size_horizontal'] = value
        self.cell_size_horizontal_text.on_trait_change(get_cell_size_horizontal,
                                                       'value')

        def get_fast(name, value):
            self.selected_values['fast'] = value
        self.fast_checkbox.on_trait_change(get_fast, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.options_box, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_bins_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_bins_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.num_or_bins_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.cell_size_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.cell_size_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.fast_checkbox, font_family, font_size, font_style,
                    font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.window_vertical_text.on_trait_change(self._render_function,
                                                      'value')
            self.window_horizontal_text.on_trait_change(self._render_function,
                                                        'value')
            self.num_bins_vertical_text.on_trait_change(self._render_function,
                                                        'value')
            self.num_bins_horizontal_text.on_trait_change(self._render_function,
                                                          'value')
            self.num_or_bins_text.on_trait_change(self._render_function,
                                                  'value')
            self.cell_size_vertical_text.on_trait_change(self._render_function,
                                                         'value')
            self.cell_size_horizontal_text.on_trait_change(
                self._render_function, 'value')
            self.fast_checkbox.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.window_vertical_text.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.window_horizontal_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.num_bins_vertical_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.num_bins_horizontal_text.on_trait_change(self._render_function,
                                                      'value', remove=True)
        self.num_or_bins_text.on_trait_change(self._render_function, 'value',
                                              remove=True)
        self.cell_size_vertical_text.on_trait_change(self._render_function,
                                                     'value', remove=True)
        self.cell_size_horizontal_text.on_trait_change(self._render_function,
                                                       'value', remove=True)
        self.fast_checkbox.on_trait_change(self._render_function, 'value',
                                           remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)


def _convert_str_to_list_int(s):
    r"""
    Function that converts a given `str` to a `list` of `int` numbers. For
    example ::

        _convert_str_to_list_int('1, 2, 3')

    returns ::

        [1, 2, 3]

    """
    if isinstance(s, str):
        return [int(i[:-1]) if i[-1] == ',' else int(i) for i in s.split()]
    else:
        return []


def _convert_str_to_list_float(s):
    r"""
    Function that converts a given `str` to a `list` of `float` numbers. For
    example ::

        _convert_str_to_list_float('1, 2, 3')

    returns ::

        [1.0, 2.0, 3.0]

    """
    if isinstance(s, str):
        return [float(i[:-1]) if i[-1] == ',' else float(i) for i in s.split()]
    else:
        return []


def _convert_int_list_to_str(l):
    r"""
    Function that converts a given `list` of `int` numbers to `str`. For
    example ::

        _convert_int_list_to_str([1, 2, 3])

    returns ::

        '1, 2, 3'

    """
    if isinstance(l, list):
        return str(l)[1:-1]
    else:
        return ''


class DaisyOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting Daisy options. Specifically, it consists of:

        1) BoundedIntText [`self.step_text`]: sampling step
        2) BoundedIntText [`self.radius_text`]: radius value
        3) BoundedIntText [`self.rings_text`]: number of rings
        4) BoundedIntText [`self.histograms_text`]: histograms
        5) BoundedIntText [`self.orientations_text`]: orientations
        6) Dropdown [`self.normalization_dropdown`]: normalization type
        7) Text [`self.sigmas_text`]: sigmas list
        8) Text [`self.ring_radii_text`]: ring radii list
        9) Box [`self.step_radius_rings_histograms_box`]: box that contains
            (1), (2), (3) and (4)
        10) Box [`self.orientations_normalization_sigmas_radii_box`]: box that
            contains (5), (6), (7) and (8)
        11) HBox [`self.options_box`]: box that contains (9) and (10)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    daisy_options : `dict`
        The initial options. Example ::

            daisy_options = {'step': 1,
                             'radius': 15,
                             'rings': 2,
                             'histograms': 2,
                             'orientations': 8,
                             'normalization': 'l1',
                             'sigmas': None,
                             'ring_radii': None}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, daisy_options, render_function=None):
        self.step_text = ipywidgets.BoundedIntText(
            value=daisy_options['step'], description='Step', min=1, max=10**6)
        self.radius_text = ipywidgets.BoundedIntText(
            value=daisy_options['radius'], description='Radius', min=1,
            max=10**6)
        self.rings_text = ipywidgets.BoundedIntText(
            value=daisy_options['rings'], description='Rings', min=1, max=10**6)
        self.histograms_text = ipywidgets.BoundedIntText(
            value=daisy_options['histograms'], description='Histograms',
            min=1, max=10**6)
        self.orientations_text = ipywidgets.BoundedIntText(
            value=daisy_options['orientations'], description='Orientations',
            min=1, max=10**6)
        tmp = OrderedDict()
        tmp['L1'] = 'l1'
        tmp['L2'] = 'l2'
        tmp['Daisy'] = 'daisy'
        tmp['None'] = None
        self.normalization_dropdown = ipywidgets.Dropdown(
            value=daisy_options['normalization'], options=tmp,
            description='Normalization')
        self.sigmas_text = ipywidgets.Text(
            value=_convert_int_list_to_str(daisy_options['sigmas']),
            description='Sigmas', width='3cm')
        self.ring_radii_text = ipywidgets.Text(
            value=_convert_int_list_to_str(daisy_options['ring_radii']),
            description='Ring radii', width='3cm')
        self.step_radius_rings_histograms_box = ipywidgets.VBox(
            children=[self.step_text, self.radius_text, self.rings_text,
                      self.histograms_text])
        self.orientations_normalization_sigmas_radii_box = ipywidgets.VBox(
            children=[self.orientations_text, self.normalization_dropdown,
                      self.sigmas_text, self.ring_radii_text])
        super(DaisyOptionsWidget, self).__init__(
            children=[self.step_radius_rings_histograms_box,
                      self.orientations_normalization_sigmas_radii_box])
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = daisy_options

        # Set functionality
        def get_step(name, value):
            self.selected_values['step'] = value
        self.step_text.on_trait_change(get_step, 'value')

        def get_radius(name, value):
            self.selected_values['radius'] = value
        self.radius_text.on_trait_change(get_radius, 'value')

        def get_rings(name, value):
            self.selected_values['rings'] = value
        self.rings_text.on_trait_change(get_rings, 'value')

        def get_histograms(name, value):
            self.selected_values['histograms'] = value
        self.histograms_text.on_trait_change(get_histograms, 'value')

        def get_orientations(name, value):
            self.selected_values['orientations'] = value
        self.orientations_text.on_trait_change(get_orientations, 'value')

        def get_normalization(name, value):
            self.selected_values['normalization'] = value
        self.normalization_dropdown.on_trait_change(get_normalization, 'value')

        def get_sigmas(name, value):
            self.selected_values['sigmas'] = \
                _convert_str_to_list_int(str(value))
        self.sigmas_text.on_trait_change(get_sigmas, 'value')

        def get_ring_radii(name, value):
            self.selected_values['ring_radii'] = \
                _convert_str_to_list_float(str(value))
        self.ring_radii_text.on_trait_change(get_ring_radii, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.step_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.radius_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.rings_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.histograms_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.orientations_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.normalization_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.sigmas_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.ring_radii_text, font_family, font_size, font_style,
                    font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.step_text.on_trait_change(self._render_function, 'value')
            self.radius_text.on_trait_change(self._render_function, 'value')
            self.rings_text.on_trait_change(self._render_function, 'value')
            self.histograms_text.on_trait_change(self._render_function, 'value')
            self.orientations_text.on_trait_change(self._render_function,
                                                   'value')
            self.normalization_dropdown.on_trait_change(self._render_function,
                                                        'value')
            self.sigmas_text.on_trait_change(self._render_function, 'value')
            self.ring_radii_text.on_trait_change(self._render_function, 'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.step_text.on_trait_change(self._render_function, 'value',
                                       remove=True)
        self.radius_text.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.rings_text.on_trait_change(self._render_function, 'value',
                                        remove=True)
        self.histograms_text.on_trait_change(self._render_function, 'value',
                                             remove=True)
        self.orientations_text.on_trait_change(self._render_function, 'value',
                                               remove=True)
        self.normalization_dropdown.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.sigmas_text.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.ring_radii_text.on_trait_change(self._render_function, 'value',
                                             remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)


class LBPOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting LBP options. Specifically, it consists of:

        1) Dropdown [`self.mapping_type_dropdown`]: select mapping type
        2) Text [`self.radius_text`]: radius list
        3) Text [`self.samples_text`]: samples list
        4) Box [`self.radius_samples_mapping_type_box`]: box that contains (2),
           (3) and (4)
        5) BoundedIntText [`self.window_vertical_text`]: window vertical step
        6) BoundedIntText [`self.window_horizontal_text`]: window horizontal
           step
        7) RadioButtons [`self.window_step_unit_radiobuttons`]: window step unit
        8) Checkbox [`self.padding_checkbox`]: padding
        9) Box [`self.window_box`]: box that contains (6), (7), (8) and (9)
        10) HBox [`self.options_box`]: box that contains (5) and (10)

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    lbp_options : `dict`
        The initial options. Example ::

        lbp_options = {'radius': range(1, 5),
                       'samples': [8] * 4,
                       'mapping_type': 'u2',
                       'window_step_vertical': 1,
                       'window_step_horizontal': 1,
                       'window_step_unit': 'pixels',
                       'padding': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, lbp_options, render_function=None):
        tmp = OrderedDict()
        tmp['Uniform-2'] = 'u2'
        tmp['Rotation-Invariant'] = 'ri'
        tmp['Both'] = 'riu2'
        tmp['None'] = 'none'
        self.mapping_type_dropdown = ipywidgets.Dropdown(
            value=lbp_options['mapping_type'], options=tmp,
            description='Mapping')
        self.radius_text = ipywidgets.Text(
            value=_convert_int_list_to_str(lbp_options['radius']),
            description='Radius')
        self.samples_text = ipywidgets.Text(
            value=_convert_int_list_to_str(lbp_options['samples']),
            description='Samples')
        self.radius_samples_mapping_type_box = ipywidgets.Box(
            children=[self.radius_text, self.samples_text,
                      self.mapping_type_dropdown])
        self.window_vertical_text = ipywidgets.BoundedIntText(
            value=lbp_options['window_step_vertical'], description='Step Y',
            min=1, max=10**6)
        self.window_horizontal_text = ipywidgets.BoundedIntText(
            value=lbp_options['window_step_horizontal'], description='Step X',
            min=1, max=10**6)
        tmp = OrderedDict()
        tmp['Pixels'] = 'pixels'
        tmp['Windows'] = 'cells'
        self.window_step_unit_radiobuttons = ipywidgets.RadioButtons(
            options=tmp, description='Step unit',
            value=lbp_options['window_step_unit'])
        self.padding_checkbox = ipywidgets.Checkbox(
            value=lbp_options['padding'], description='Padding')
        self.window_box = ipywidgets.Box(
            children=[self.window_vertical_text, self.window_horizontal_text,
                      self.window_step_unit_radiobuttons,
                      self.padding_checkbox])
        super(LBPOptionsWidget, self).__init__(
            children=[self.window_box, self.radius_samples_mapping_type_box])
        self.orientation = 'horizontal'

        # Assign output
        self.selected_values = lbp_options

        # Set functionality
        def get_mapping_type(name, value):
            self.selected_values['mapping_type'] = value
        self.mapping_type_dropdown.on_trait_change(get_mapping_type, 'value')

        def get_window_vertical(name, value):
            self.selected_values['window_step_vertical'] = value
        self.window_vertical_text.on_trait_change(get_window_vertical, 'value')

        def get_window_horizontal(name, value):
            self.selected_values['window_step_horizontal'] = value
        self.window_horizontal_text.on_trait_change(get_window_horizontal,
                                                    'value')

        def get_window_step_unit(name, value):
            self.selected_values['window_step_unit'] = value
        self.window_step_unit_radiobuttons.on_trait_change(get_window_step_unit,
                                                           'value')

        def get_padding(name, value):
            self.selected_values['padding'] = value
        self.padding_checkbox.on_trait_change(get_padding, 'value')

        def get_radius(name, value):
            self.selected_values['radius'] = \
                _convert_str_to_list_int(str(value))
        self.radius_text.on_trait_change(get_radius, 'value')

        def get_samples(name, value):
            self.selected_values['samples'] = \
                _convert_str_to_list_int(str(value))
        self.samples_text.on_trait_change(get_samples, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.mapping_type_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.radius_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.samples_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.window_vertical_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_horizontal_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.window_step_unit_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.padding_checkbox, font_family, font_size, font_style,
                    font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.mapping_type_dropdown.on_trait_change(self._render_function,
                                                       'value')
            self.radius_text.on_trait_change(self._render_function, 'value')
            self.samples_text.on_trait_change(self._render_function, 'value')
            self.window_vertical_text.on_trait_change(self._render_function,
                                                      'value')
            self.window_horizontal_text.on_trait_change(self._render_function,
                                                        'value')
            self.window_step_unit_radiobuttons.on_trait_change(
                self._render_function, 'value')
            self.padding_checkbox.on_trait_change(self._render_function,
                                                  'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.mapping_type_dropdown.on_trait_change(self._render_function,
                                                   'value', remove=True)
        self.radius_text.on_trait_change(self._render_function, 'value',
                                         remove=True)
        self.samples_text.on_trait_change(self._render_function, 'value',
                                          remove=True)
        self.window_vertical_text.on_trait_change(self._render_function,
                                                  'value', remove=True)
        self.window_horizontal_text.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self.window_step_unit_radiobuttons.on_trait_change(
            self._render_function, 'value', remove=True)
        self.padding_checkbox.on_trait_change(self._render_function, 'value',
                                              remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)


class IGOOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting IGO options. Specifically, it consists of:

        1) Checkbox [`self.double_angles_checkbox`]: enable double angles

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    igo_options : `dict`
        The initial options. Example ::

        igo_options = {'double_angles': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """
    def __init__(self, igo_options, render_function=None):
        self.double_angles_checkbox = ipywidgets.Checkbox(
            value=igo_options['double_angles'], description='Double angles')
        super(IGOOptionsWidget, self).__init__(
            children=[self.double_angles_checkbox])

        # Assign output
        self.selected_values = igo_options

        # Set functionality
        def get_double_angles(name, value):
            self.selected_values['double_angles'] = value
        self.double_angles_checkbox.on_trait_change(get_double_angles, 'value')

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Widget style options ::

                {'success', 'info', 'warning', 'danger', ''}
                or
                None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy',
                 'monospace', 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book',
                 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold',
                 'heavy', 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.double_angles_checkbox, font_family, font_size,
                    font_style, font_weight)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.double_angles_checkbox.on_trait_change(self._render_function,
                                                        'value')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        self.double_angles_checkbox.on_trait_change(self._render_function,
                                                    'value', remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback. If ``None``, then
            nothing is happening.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)
