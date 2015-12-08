import ipywidgets
from traitlets.traitlets import Int, Dict
from traitlets import link
from collections import OrderedDict

from .abstract import MenpoWidget
from .tools import (IndexSliderWidget, IndexButtonsWidget, SlicingCommandWidget,
                    LineOptionsWidget, MarkerOptionsWidget,
                    NumberingOptionsWidget, LegendOptionsWidget,
                    ZoomOneScaleWidget, ZoomTwoScalesWidget, AxesOptionsWidget,
                    GridOptionsWidget, ImageOptionsWidget,
                    ColourSelectionWidget)
from .style import map_styles_to_hex_colours, format_box, format_font


class AnimationOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for animating through a list of objects. The widget
    consists of the following parts from `ipywidgets` and `menpowidgets.tools`:

    == ================== ===================== ====================
    No Object             Variable (`self.`)    Description
    == ================== ===================== ====================
    1  ToggleButton       `play_stop_toggle`    The play/stop button
    2  ToggleButton       `play_options_toggle` Button that toggles

                                                the options menu
    3  Checkbox           `loop_checkbox`       Repeat mode
    4  FloatText          `interval_text`       Interval (secs)
    5  VBox               `loop_interval_box`   Contains 3, 4
    6  VBox               `play_options_box`    Contains 2, 5
    7  HBox               `animation_box`       Contains 1, 6
    8  IndexButtonsWidget `index_wid`           The index selector

       IndexSliderWidget                        widget
    == ================== ===================== ====================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` and ``replace_update_function()`` methods.

    Parameters
    ----------
    index : `dict`
        The dictionary with the initial options. For example
        ::

            index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    index_style : ``{'buttons', 'slider'}``, optional
        If ``'buttons'``, then `IndexButtonsWidget()` class is called. If
        ``'slider'``, then 'IndexSliderWidget()' class is called.
    interval : `float`, optional
        The interval between the animation progress.
    description : `str`, optional
        The title of the widget.
    loop_enabled : `bool`, optional
        If ``True``, then after reach the minimum (maximum) index values, the
        counting will continue from the end (beginning). If ``False``, the
        counting will stop at the minimum (maximum) value.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    continuous_update : `bool`, optional
        If ``True`` and `index_style` is set to ``'slider'``, then the render
        and update functions are called while moving the slider's handle. If
        ``False``, then the the functions are called only when the handle
        (mouse click) is released.

    Example
    -------
    Let's create an animation widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import AnimationOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Selected index: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}
        >>> wid = AnimationOptionsWidget(index, index_style='buttons',
        >>>                              render_function=render_function,
        >>>                              style='info')
        >>> wid

    By pressing the buttons (or simply pressing the Play button), the printed
    message gets updated. Finally, let's change the widget status with a new
    dictionary of options:

        >>> new_options = {'min': 0, 'max': 20, 'step': 2, 'index': 16}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, index, render_function=None, index_style='buttons',
                 interval=0.2, description='Index: ', loop_enabled=True,
                 style='minimal', continuous_update=False):
        from time import sleep
        from IPython import get_ipython

        # Get the kernel to use it later in order to make sure that the widgets'
        # traits changes are passed during a while-loop
        kernel = get_ipython().kernel

        # Create index widget
        if index_style == 'slider':
            self.index_wid = IndexSliderWidget(
                index, description=description,
                continuous_update=continuous_update)
        elif index_style == 'buttons':
            self.index_wid = IndexButtonsWidget(
                index, description=description, minus_description='fa-minus',
                plus_description='fa-plus', loop_enabled=loop_enabled,
                text_editable=True)
        else:
            raise ValueError('index_style should be either slider or buttons')
        self.index_wid.style(box_style=None, border_visible=False,
                             padding=0, margin='0.1cm')

        # Create other widgets
        self.play_stop_toggle = ipywidgets.ToggleButton(
            icon='fa-play', description='', value=False, margin='0.1cm')
        self._toggle_play_style = 'success'
        self._toggle_stop_style = 'danger'
        if style == 'minimal':
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        self.play_options_toggle = ipywidgets.ToggleButton(
            icon='fa-wrench', description='', value=False, margin='0.1cm')
        self.loop_checkbox = ipywidgets.Checkbox(
            description='Loop', value=loop_enabled)
        self.interval_text = ipywidgets.FloatText(description='Interval (sec)',
                                                  value=interval, width='1.4cm')
        self.loop_interval_box = ipywidgets.VBox(
            children=[self.interval_text, self.loop_checkbox], visible=False,
            margin='0.1cm', padding='0.1cm', border_color='black',
            border_style='solid', border_width=1)
        self.play_options_box = ipywidgets.HBox(
            children=[self.play_options_toggle, self.loop_interval_box])
        self.animation_box = ipywidgets.HBox(
            children=[self.play_stop_toggle, self.play_options_box])

        # Create final widget
        children = [self.index_wid, self.animation_box]
        super(AnimationOptionsWidget, self).__init__(
            children, Int, index['index'], render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']
        self.loop_enabled = loop_enabled
        self.index_style = index_style
        self.continuous_update = continuous_update

        # Set style
        self.predefined_style(style)

        # Set functionality
        def play_stop_pressed(name, value):
            if value:
                # Animation was not playing, so Play was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_stop_style
                # Change the description to Stop
                self.play_stop_toggle.icon = 'fa-stop'
                # Make sure that play options are off
                self.play_options_toggle.value = False
            else:
                # Animation was playing, so Stop was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_play_style
                # Change the description to Play
                self.play_stop_toggle.icon = 'fa-play'
            self.play_options_toggle.disabled = value
        self.play_stop_toggle.on_trait_change(play_stop_pressed, 'value')

        def play_options_visibility(name, value):
            self.loop_interval_box.visible = value
        self.play_options_toggle.on_trait_change(play_options_visibility,
                                                 'value')

        def animate(name, value):
            if self.loop_checkbox.value:
                # loop is enabled
                i = self.selected_values
                if i < self.max:
                    i += self.step
                else:
                    i = self.min

                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    if i < self.max:
                        i += self.step
                    else:
                        i = self.min

                    # wait
                    sleep(self.interval_text.value)
            else:
                # loop is disabled
                i = self.selected_values
                i += self.step
                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    i += self.step

                    # wait
                    sleep(self.interval_text.value)
                if i > self.max:
                    self.play_stop_toggle.value = False
        self.play_stop_toggle.on_trait_change(animate, 'value')

        def save_value(name, value):
            self.selected_values = self.index_wid.selected_values
        self.index_wid.on_trait_change(save_value, 'selected_values')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.play_stop_toggle, font_family, font_size, font_style,
                    font_weight)
        format_font(self.play_options_toggle, font_family, font_size,
                    font_style, font_weight)
        format_font(self.loop_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.interval_text, font_family, font_size, font_style,
                    font_weight)
        if self.index_style == 'buttons':
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)
        else:
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style='', border_visible=False)
            self.play_stop_toggle.button_style = ''
            self.play_stop_toggle.font_weight = 'normal'
            self.play_options_toggle.button_style = ''
            format_box(self.loop_interval_box, '', False, 'black', 'solid', 1,
                       10, '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = ''
                self.index_wid.button_plus.font_weight = 'normal'
                self.index_wid.button_minus.button_style = ''
                self.index_wid.button_minus.font_weight = 'normal'
                self.index_wid.index_text.background_color = None
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = None
                self.index_wid.slider.background_color = None
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        elif (style == 'info' or style == 'success' or style == 'danger' or
              style == 'warning'):
            self.style(box_style=style, border_visible=False)
            self.play_stop_toggle.button_style = 'success'
            self.play_stop_toggle.font_weight = 'bold'
            self.play_options_toggle.button_style = 'info'
            format_box(self.loop_interval_box, 'info', True,
                       map_styles_to_hex_colours('info'), 'solid', 1, 10,
                       '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = 'primary'
                self.index_wid.button_plus.font_weight = 'bold'
                self.index_wid.button_minus.button_style = 'primary'
                self.index_wid.button_minus.font_weight = 'bold'
                self.index_wid.index_text.background_color = \
                    map_styles_to_hex_colours(style, True)
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = \
                    map_styles_to_hex_colours(style)
                self.index_wid.slider.background_color = \
                    map_styles_to_hex_colours(style)
            self._toggle_play_style = 'success'
            self._toggle_stop_style = 'danger'
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, index, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        index : `dict`
            The dictionary with the new options to be used. For example
            ::

                index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update
        if self.play_stop_toggle.value:
            self.play_stop_toggle.value = False
        if self.index_style == 'slider':
            self.index_wid.set_widget_state(
                index, continuous_update=self.continuous_update,
                allow_callback=False)
        else:
            self.index_wid.set_widget_state(
                index, loop_enabled=self.loop_checkbox.value,
                text_editable=True, allow_callback=False)
        self.selected_values = index['index']
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', 0)


class ChannelOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting channel options when rendering an image. The
    widget consists of the following parts from `ipywidgets`:

    == ==================== ============================= =====================
    No Object               Variable (`self.`)            Description
    == ==================== ============================= =====================
    1  SlicingCommandWidget `channels_wid`                The channels selector
    2  Checkbox             `masked_checkbox`             Controls masked mode
    3  Checkbox             `rgb_checkbox`                View as RGB
    4  Checkbox             `sum_checkbox`                View sum of channels
    5  Checkbox             `glyph_checkbox`              View glyph
    6  BoundedIntText       `glyph_block_size_text`       Glyph block size
    7  Checkbox             `glyph_use_negative_checkbox` Use negative values
    8  VBox                 `glyph_options_box`           Contains 6, 7
    9  VBox                 `glyph_box`                   Contains 5, 8
    10 HBox                 `rgb_masked_options_box`      Contains 2, 3
    11 HBox                 `glyph_sum_options_box`       Contains 4, 9
    12 VBox                 `checkboxes_box`              Contains 10, 11
    13 Latex                `no_options_latex`            No options available
    == ==================== ============================= =====================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` method.

    Parameters
    ----------
    channel_options : `dict`
        The dictionary with the initial options. For example
        ::

            channel_options = {'n_channels': 10,
                               'image_is_masked': True,
                               'channels': 0,
                               'glyph_enabled': False,
                               'glyph_block_size': 3,
                               'glyph_use_negative': False,
                               'sum_enabled': False,
                               'masked_enabled': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create a channels widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import ChannelOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected channels and masked flag:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Channels: {}, Masked: {}".format(
        >>>         wid.selected_values['channels'],
        >>>         wid.selected_values['masked_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> channel_options = {'n_channels': 30,
        >>>                    'image_is_masked': True,
        >>>                    'channels': [0, 10],
        >>>                    'glyph_enabled': False,
        >>>                    'glyph_block_size': 3,
        >>>                    'glyph_use_negative': False,
        >>>                    'sum_enabled': True,
        >>>                    'masked_enabled': True}
        >>> wid = ChannelOptionsWidget(channel_options,
        >>>                            render_function=render_function,
        >>>                            style='warning')
        >>> wid

    By playing around with the widget, printed message gets updated. Finally,
    let's change the widget status with a new dictionary of options:

        >>> new_options = {'n_channels': 10,
        >>>                'image_is_masked': True,
        >>>                'channels': [7, 8, 9],
        >>>                'glyph_enabled': True,
        >>>                'glyph_block_size': 3,
        >>>                'glyph_use_negative': True,
        >>>                'sum_enabled': False,
        >>>                'masked_enabled': False}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, channel_options, render_function=None, style='minimal'):
        # Parse given options
        channel_options, channels = self._parse_options_dict(channel_options)

        # Create children
        slice_options = {'command': channels,
                         'length': channel_options['n_channels']}
        self.channels_wid = SlicingCommandWidget(
            slice_options, description='Channels:', render_function=None,
            example_visible=True, continuous_update=False,
            orientation='horizontal')
        self.masked_checkbox = ipywidgets.Checkbox(
            value=channel_options['masked_enabled'], description='Masked',
            margin='0.1cm')
        self.rgb_checkbox = ipywidgets.Checkbox(
            value=(channel_options['n_channels'] == 3 and
                   channel_options['channels'] is None),
            description='RGB', margin='0.1cm')
        self.sum_checkbox = ipywidgets.Checkbox(
            value=channel_options['sum_enabled'], description='Sum',
            margin='0.1cm')
        self.glyph_checkbox = ipywidgets.Checkbox(
            value=channel_options['glyph_enabled'], description='Glyph',
            margin='0.1cm')
        self.glyph_block_size_text = ipywidgets.BoundedIntText(
            description='Block size', min=1, max=25,
            value=channel_options['glyph_block_size'], width='1.5cm')
        self.glyph_use_negative_checkbox = ipywidgets.Checkbox(
            description='Negative', value=channel_options['glyph_use_negative'])
        self.no_options_latex = ipywidgets.Latex(value='No options available')

        # Group widgets
        self.glyph_options_box = ipywidgets.VBox(
            children=[self.glyph_block_size_text,
                      self.glyph_use_negative_checkbox],
            visible=channel_options['glyph_enabled'], margin='0.1cm')
        self.glyph_box = ipywidgets.HBox(children=[self.glyph_checkbox,
                                                   self.glyph_options_box],
                                         align='start')
        self.rgb_masked_options_box = ipywidgets.HBox(
            children=[self.rgb_checkbox, self.masked_checkbox])
        self.glyph_sum_options_box = ipywidgets.HBox(
            children=[self.sum_checkbox, self.glyph_box])
        self.checkboxes_box = ipywidgets.VBox(
            children=[self.rgb_masked_options_box, self.glyph_sum_options_box])

        # Create final widget
        children = [self.channels_wid, self.checkboxes_box,
                    self.no_options_latex]
        initial_dict = {
            'channels': channel_options['channels'],
            'glyph_enabled': channel_options['glyph_enabled'],
            'glyph_block_size': channel_options['glyph_block_size'],
            'glyph_use_negative': channel_options['glyph_use_negative'],
            'sum_enabled': channel_options['sum_enabled'],
            'masked_enabled': channel_options['masked_enabled']}
        super(ChannelOptionsWidget, self).__init__(
            children, Dict, initial_dict, render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.n_channels = channel_options['n_channels']
        self.image_is_masked = channel_options['image_is_masked']

        # Set widget's visibility
        self.set_visibility()

        # Set style
        self.predefined_style(style)

        # Set functionality
        def save_options(name, value):
            channels_val = self.channels_wid.selected_values
            if self.rgb_checkbox.value:
                channels_val = None
            self.selected_values = {
                'channels': channels_val,
                'glyph_enabled': self.glyph_checkbox.value,
                'glyph_block_size': self.glyph_block_size_text.value,
                'glyph_use_negative': self.glyph_use_negative_checkbox.value,
                'sum_enabled': self.sum_checkbox.value,
                'masked_enabled': self.masked_checkbox.value}
        self.glyph_block_size_text.on_trait_change(save_options, 'value')
        self.glyph_use_negative_checkbox.on_trait_change(save_options, 'value')
        self.masked_checkbox.on_trait_change(save_options, 'value')

        def save_channels(name, value):
            if self.n_channels == 3:
                # temporarily remove rgb callback
                self.rgb_checkbox.on_trait_change(save_rgb, 'value', remove=True)
                # set value
                self.rgb_checkbox.value = False
                # re-assign rgb callback
                self.rgb_checkbox.on_trait_change(save_rgb, 'value')
            save_options('', None)
        self.channels_wid.on_trait_change(save_channels, 'selected_values')

        def save_rgb(name, value):
            if value:
                # temporarily remove channels callback
                self.channels_wid.on_trait_change(save_channels,
                                                  'selected_values', remove=True)
                # update channels widget
                self.channels_wid.set_widget_state(
                    {'command': '0, 1, 2', 'length': self.n_channels},
                    allow_callback=False)
                # re-assign channels callback
                self.channels_wid.on_trait_change(save_channels,
                                                  'selected_values')
            save_options('', None)
        self.rgb_checkbox.on_trait_change(save_rgb, 'value')

        def save_sum(name, value):
            if value and self.glyph_checkbox.value:
                # temporarily remove glyph callback
                self.glyph_checkbox.on_trait_change(save_glyph, 'value',
                                                    remove=True)

                # set glyph to False
                self.glyph_checkbox.value = False
                self.glyph_options_box.visible = False

                # re-assign glyph callback
                self.glyph_checkbox.on_trait_change(save_glyph, 'value')
            save_options('', None)
        self.sum_checkbox.on_trait_change(save_sum, 'value')

        def save_glyph(name, value):
            if value and self.sum_checkbox.value:
                # temporarily remove sum callback
                self.sum_checkbox.on_trait_change(save_sum, 'value',
                                                  remove=True)

                # set glyph to false
                self.sum_checkbox.value = False

                # re-assign sum callback
                self.sum_checkbox.on_trait_change(save_sum, 'value')
            # set visibility
            self.glyph_options_box.visible = value
            save_options('', None)
        self.glyph_checkbox.on_trait_change(save_glyph, 'value')

    def set_visibility(self):
        self.channels_wid.visible = self.n_channels > 1
        self.glyph_sum_options_box.visible = self.n_channels > 1
        self.rgb_checkbox.visible = self.n_channels == 3
        self.masked_checkbox.visible = self.image_is_masked
        self.no_options_latex.visible = (self.n_channels == 1 and
                                         not self.image_is_masked)

    def _parse_options_dict(self, channel_options):
        # If image_is_masked is False, then masked_enabled should be False too
        if not channel_options['image_is_masked']:
            channel_options['masked_enabled'] = False

        # Parse channels
        if channel_options['channels'] is None:
            channels_val = '0, 1, 2'
        elif isinstance(channel_options['channels'], list):
            channels_val = str(channel_options['channels']).strip('[]')
        else:
            channels_val = str(channel_options['channels'])

        # Parse sum, glyph
        if (channel_options['n_channels'] == 1 or
                (channel_options['sum_enabled'] and
                     channel_options['glyph_enabled'])):
            channel_options['sum_enabled'] = False
            channel_options['glyph_enabled'] = False
        return channel_options, channels_val

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='4cm'):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        slider_width : `str`, optional
            The width of the slider.
        slider_colour : `str`, optional
            The colour of the sliders.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        self.channels_wid.single_slider.width = slider_width
        self.channels_wid.multiple_slider.width = slider_width
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.rgb_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.masked_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.sum_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.glyph_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.glyph_block_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.glyph_use_negative_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.no_options_latex, font_family, font_size, font_style,
                    font_weight)
        self.channels_wid.style(
            box_style=box_style, border_visible=False, text_box_style=None,
            text_box_background_colour=None, text_box_width=None,
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', slider_width='4cm')
            format_box(self.glyph_options_box, box_style='',
                       border_visible=False, border_colour='',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.1cm', margin=0)
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       slider_width='4cm')
            format_box(self.glyph_options_box, box_style=style,
                       border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.1cm', margin=0)
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, channel_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        channel_options : `dict`
            The dictionary with the new options to be used. For example
            ::

                channel_options = {'n_channels': 10,
                                   'image_is_masked': True,
                                   'channels': 0,
                                   'glyph_enabled': False,
                                   'glyph_block_size': 3,
                                   'glyph_use_negative': False,
                                   'sum_enabled': False,
                                   'masked_enabled': True}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # Parse given options
        channel_options, channels = self._parse_options_dict(channel_options)

        # Set both sum and glyph to False, to make sure that there is no conflict
        self.sum_checkbox.value = False
        self.glyph_checkbox.value = False

        # Update widgets' state
        self.n_channels = channel_options['n_channels']
        self.image_is_masked = channel_options['image_is_masked']
        slice_options = {'command': channels,
                         'length': channel_options['n_channels']}
        self.channels_wid.set_widget_state(slice_options, allow_callback=False)
        self.masked_checkbox.value = channel_options['masked_enabled']
        self.rgb_checkbox.value = (channel_options['n_channels'] == 3 and
                                   channel_options['channels'] is None)
        self.sum_checkbox.value = channel_options['sum_enabled']
        self.glyph_checkbox.value = channel_options['glyph_enabled']
        self.glyph_block_size_text.value = channel_options['glyph_block_size']
        self.glyph_use_negative_checkbox.value = \
            channel_options['glyph_use_negative']

        # Set widget's visibility
        self.set_visibility()

        # Re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class LandmarkOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for animating through a list of objects. The widget
    consists of the following parts from `ipywidgets`:

    == ============= =========================== =========================
    No Object        Variable (`self.`)               Description
    == ============= =========================== =========================
    1  Latex         `no_landmarks_msg`          Message in case there are

                                                 no landmarks available.
    2  Checkbox      `render_landmarks_checkbox` Render landmarks
    3  Latex         `group_description`         Landmark group title
    4  IntSlider     `group_slider`              Landmark group selector
    5  Dropdown      `group_dropdown`            Landmark group selector
    6  Latex         `labels_text`               Labels title
    7  ToggleButtons `labels_toggles`            `list` of `lists` with

                                                 the labels per group
    8  HBox          `group_selection_box`       Contains 3, 4, 5
    9  HBox          `labels_and_text_box`       Contains 6 and all 7
    10 VBox          `options_box`               Contains 8, 9
    11 HBox          `render_and_options_box`    Contains 2, 10
    == ============= =========================== =========================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` and ``replace_update_function()`` methods.

    Parameters
    ----------
    landmark_options : `dict`
        The dictionary with the initial options. For example
        ::

            landmark_options = {'has_landmarks': True,
                                'render_landmarks': True,
                                'group_keys': ['PTS', 'ibug_face_68'],
                                'labels_keys': [['all'], ['jaw', 'eye']],
                                'group': 'PTS',
                                'with_labels': ['all']}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    style : `str` (see below)
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create a landmarks widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import LandmarkOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Group: {}, Labels: {}".format(
        >>>         wid.selected_values['group'],
        >>>         wid.selected_values['with_labels'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> landmark_options = {'has_landmarks': True,
        >>>                     'render_landmarks': True,
        >>>                     'group_keys': ['PTS', 'ibug_face_68'],
        >>>                     'labels_keys': [['all'], ['jaw', 'eye', 'mouth']],
        >>>                     'group': 'ibug_face_68',
        >>>                     'with_labels': ['eye', 'jaw', 'mouth']}
        >>> wid = LandmarkOptionsWidget(landmark_options,
        >>>                             render_function=render_function,
        >>>                             style='danger')
        >>> wid

    By playing around with the widget, the printed message gets updated.
    Finally, let's change the widget status with a new dictionary of options:

        >>> new_options = {'has_landmarks': True,
        >>>                'render_landmarks': True,
        >>>                'group_keys': ['new_group'],
        >>>                'labels_keys': [['1', '2', '3']],
        >>>                'group': 'new_group',
        >>>                'with_labels': None}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, landmark_options, render_function=None,
                 style='minimal'):
        # Parse given options
        landmark_options, group_idx = self._parse_landmark_options_dict(
            landmark_options)

        # Create children
        # Render landmarks checkbox and no landmarks message
        self.no_landmarks_msg = ipywidgets.Latex(
            value='No landmarks available.')
        self.render_landmarks_checkbox = ipywidgets.Checkbox(
            description='Render landmarks',
            value=landmark_options['render_landmarks'], margin='0.3cm')

        # Create group description, dropdown and slider
        self.group_description = ipywidgets.Latex(value='Group', margin='0.1cm')
        dropdown_dict = OrderedDict()
        for gn, gk in enumerate(landmark_options['group_keys']):
            dropdown_dict[gk] = gn
        self.group_slider = ipywidgets.IntSlider(
            min=0, max=len(landmark_options['group_keys']) - 1, margin='0.1cm',
            font_size=0, value=group_idx, width='3cm', continuous_update=False)
        self.group_dropdown = ipywidgets.Dropdown(
            options=dropdown_dict, description='', value=group_idx,
            margin='0.1cm')
        self.group_selection_box = ipywidgets.HBox(
            children=[self.group_description, self.group_slider,
                      self.group_dropdown], align='center')
        # Link the values of group dropdown and slider
        self.link_group_dropdown_and_slider = link(
            (self.group_dropdown, 'value'), (self.group_slider, 'value'))
        # Create labels
        self.labels_toggles = [
            [ipywidgets.ToggleButton(description=k, value=True) for k in s_keys]
            for s_keys in landmark_options['labels_keys']]
        self.labels_text = ipywidgets.Latex(value='Labels')
        self.labels_box = ipywidgets.HBox(
            children=self.labels_toggles[group_idx], padding='0.3cm')
        self.labels_and_text_box = ipywidgets.HBox(
            children=[self.labels_text, self.labels_box], align='center')
        self._set_labels_toggles_values(landmark_options['with_labels'])
        self.options_box = ipywidgets.VBox(
            children=[self.group_selection_box, self.labels_and_text_box],
            margin='0.2cm')
        self.render_and_options_box = ipywidgets.HBox(
            children=[self.render_landmarks_checkbox, self.options_box])

        # Create final widget
        children = [self.render_and_options_box, self.no_landmarks_msg]
        initial_dict = {
            'with_labels': landmark_options['with_labels'],
            'render_landmarks': landmark_options['render_landmarks'],
            'group': landmark_options['group']}
        super(LandmarkOptionsWidget, self).__init__(
            children, Dict, initial_dict, render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.has_landmarks = landmark_options['has_landmarks']
        self.group_keys = landmark_options['group_keys']
        self.labels_keys = landmark_options['labels_keys']

        # Set widget's visibility
        self.set_visibility()

        # Set style
        self.predefined_style(style)

        # Set functionality
        def save_options(name, value):
            self.selected_values = {
                'group': self.group_keys[self.group_dropdown.value],
                'render_landmarks': self.render_landmarks_checkbox.value,
                'with_labels': self._get_with_labels()}

        def render_landmarks_fun(name, value):
            # If render is True, then check whether all the labels are disabled.
            # If they are, then enable all of them
            if value:
                if len(self._get_with_labels()) == 0:
                    for ww in self.labels_box.children:
                        # temporarily remove render function
                        ww.on_trait_change(labels_fun, 'value', remove=True)
                        # set value
                        ww.value = True
                        # re-add render function
                        ww.on_trait_change(labels_fun, 'value')
            # set visibility
            self.options_box.visible = value
            # save options
            save_options('', None)
        self.render_landmarks_checkbox.on_trait_change(render_landmarks_fun,
                                                       'value')

        def group_fun(name, value):
            # assign the correct children to the labels toggles
            self.labels_box.children = self.labels_toggles[value]
            # save options
            save_options('', None)
        self.group_dropdown.on_trait_change(group_fun, 'value')

        def labels_fun(name, value):
            # if all labels toggles are False, set render landmarks checkbox to
            # False
            if len(self._get_with_labels()) == 0:
                # temporarily remove render function
                self.render_landmarks_checkbox.on_trait_change(
                    render_landmarks_fun, 'value', remove=True)
                # set value
                self.render_landmarks_checkbox.value = False
                # set visibility
                self.options_box.visible = False
                # re-add render function
                self.render_landmarks_checkbox.on_trait_change(
                    render_landmarks_fun, 'value')
            # save options
            save_options('', None)
        # assign labels_fun to all labels toggles (even hidden ones)
        self._add_function_to_labels_toggles(labels_fun)

        # Store functions
        self._render_landmarks_fun = render_landmarks_fun
        self._group_fun = group_fun
        self._labels_fun = labels_fun

    def _parse_landmark_options_dict(self, landmark_options):
        if landmark_options['group'] is None:
            landmark_options['group'] = landmark_options['group_keys'][0]
        if (len(landmark_options['group_keys']) == 1 and
                landmark_options['group_keys'][0] == ' '):
            landmark_options['has_landmarks'] = False
        if not landmark_options['has_landmarks']:
            landmark_options['render_landmarks'] = False
            landmark_options['group_keys'] = [' ']
            landmark_options['group'] = ' '
            landmark_options['labels_keys'] = [[' ']]
            landmark_options['with_labels'] = [' ']
            group_idx = 0
        else:
            # Get selected group value index
            group_idx = landmark_options['group_keys'].index(
                landmark_options['group'])
            if landmark_options['with_labels'] is None:
                landmark_options['with_labels'] = \
                    landmark_options['labels_keys'][group_idx]
            elif len(landmark_options['with_labels']) == 0:
                landmark_options['render_landmarks'] = False
        return landmark_options, group_idx

    def set_visibility(self):
        # control group visibility
        self.group_slider.visible = len(self.group_keys) > 1
        self.group_dropdown.disabled = not len(self.group_keys) > 1
        # has landmarks visibility
        self.no_landmarks_msg.visible = not self.has_landmarks
        self.render_and_options_box.visible = self.has_landmarks
        # render_landmarks visibility
        self.options_box.visible = self.selected_values['render_landmarks']

    def _get_with_labels(self):
        with_labels = []
        for ww in self.labels_box.children:
            if ww.value:
                with_labels.append(str(ww.description))
        return with_labels

    def _add_function_to_labels_toggles(self, fun):
        for s_group in self.labels_toggles:
            for w in s_group:
                w.on_trait_change(fun, 'value')

    def _remove_function_from_labels_toggles(self, fun):
        for s_group in self.labels_toggles:
            for w in s_group:
                w.on_trait_change(fun, 'value', remove=True)

    def _set_labels_toggles_values(self, with_labels):
        for w in self.labels_box.children:
            w.value = w.description in with_labels

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', labels_buttons_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        labels_buttons_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'primary' Blue-based style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_landmarks_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.group_dropdown, font_family, font_size, font_style,
                    font_weight)
        format_font(self.group_description, font_family, font_size, font_style,
                    font_weight)
        for s_group in self.labels_toggles:
            for w in s_group:
                format_font(w, font_family, font_size, font_style, font_weight)
                w.button_style = labels_buttons_style
        format_font(self.labels_text, font_family, font_size, font_style,
                    font_weight)
        self.group_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.group_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', labels_buttons_style='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       labels_buttons_style='primary')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def _compare_groups_and_labels(self, groups, labels):
        r"""
        Function that compares the provided landmarks groups and labels with
        `self.selected_values['group_keys']` and
        `self.selected_values['labels_keys']`.

        Parameters
        ----------
        groups : `list` of `str`
            The new `list` of landmark groups.
        labels : `list` of `list` of `str`
            The new `list` of `list`s of each landmark group's labels.

        Returns
        -------
        _compare_groups_and_labels : `bool`
            ``True`` if the groups and labels are identical with the ones stored
            in `self.selected_values['group_keys']` and
            `self.selected_values['labels_keys']`.
        """
        # function that compares two lists without taking into account the order
        def comp_lists(l1, l2):
            len_match = len(l1) == len(l2)
            return len_match and all([g1 == g2 for g1, g2 in zip(l1, l2)])

        # comparison of the given groups
        groups_same = comp_lists(groups, self.group_keys)

        # if groups are the same, then compare the labels
        if groups_same:
            len_match = len(labels) == len(self.labels_keys)
            tmp = [comp_lists(g1, g2)
                   for g1, g2 in zip(labels, self.labels_keys)]
            return len_match and all(tmp)
        else:
            return False

    def set_widget_state(self, landmark_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        landmark_options : `dict`
            The dictionary with the new options to be used. For example
            ::

                landmark_options = {'has_landmarks': True,
                                    'render_landmarks': True,
                                    'group_keys': ['PTS', 'ibug_face_68'],
                                    'labels_keys': [['all'], ['jaw', 'eye']],
                                    'group': 'PTS',
                                    'with_labels': ['all']}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Parse given options
        landmark_options, group_idx = self._parse_landmark_options_dict(
            landmark_options)

        # Check if group_keys and labels_keys are the same with the existing
        # ones
        if not self._compare_groups_and_labels(landmark_options['group_keys'],
                                               landmark_options['labels_keys']):
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # temporarily remove the rest of the callbacks
            self.render_landmarks_checkbox.on_trait_change(
                self._render_landmarks_fun, 'value', remove=True)
            self.group_dropdown.on_trait_change(self._group_fun, 'value',
                                                remove=True)
            self._remove_function_from_labels_toggles(self._labels_fun)

            # Update widgets' state
            self.group_slider.min = 0
            self.group_slider.max = len(landmark_options['group_keys']) - 1
            dropdown_dict = OrderedDict()
            for gn, gk in enumerate(landmark_options['group_keys']):
                dropdown_dict[gk] = gn
            self.group_dropdown.options = dropdown_dict
            if (group_idx == self.group_dropdown.value and
                    len(landmark_options['group_keys']) > 1):
                if self.group_dropdown.value == 0:
                    self.group_dropdown.value = 1
                else:
                    self.group_dropdown.value = 0
            self.group_dropdown.value = group_idx
            self.labels_toggles = [
                [ipywidgets.ToggleButton(description=k, value=True)
                 for k in s_keys]
                for s_keys in landmark_options['labels_keys']]
            self.labels_box.children = self.labels_toggles[group_idx]
            self._set_labels_toggles_values(landmark_options['with_labels'])
            self.render_landmarks_checkbox.value = \
                landmark_options['render_landmarks']

            # Assign properties
            self.has_landmarks = landmark_options['has_landmarks']
            self.group_keys = landmark_options['group_keys']
            self.labels_keys = landmark_options['labels_keys']

            # Set widget's visibility
            self.set_visibility()

            # Re-assign render callback
            self.add_render_function(render_function)

            # Re-assign the rest of the callbacks
            self.render_landmarks_checkbox.on_trait_change(
                self._render_landmarks_fun, 'value')
            self.group_dropdown.on_trait_change(self._group_fun, 'value')
            self._add_function_to_labels_toggles(self._labels_fun)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class TextPrintWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for printing text. Specifically, it consists of a `list`
    of `IPython.html.widgets.Latex` objects, i.e. one per text line.

    Note that:

    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.

    Parameters
    ----------
    n_lines : `int`
        The number of lines of the text to be printed.
    text_per_line : `list` of length `n_lines`
        The text to be printed per line.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create an text widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import TextPrintWidget

    Create the widget with some initial options and display it:

        >>> n_lines = 3
        >>> text_per_line = ['> The', '> Menpo', '> Team']
        >>> wid = TextPrintWidget(n_lines, text_per_line, style='success')
        >>> wid

    The style of the widget can be changed as:

        >>> wid.predefined_style('danger')

    Update the widget state as:

        >>> wid.set_widget_state(5, ['M', 'E', 'N', 'P', 'O'])
    """
    def __init__(self, n_lines, text_per_line, style='minimal'):
        self.latex_texts = [ipywidgets.Latex(value=text_per_line[i])
                            for i in range(n_lines)]
        super(TextPrintWidget, self).__init__(children=self.latex_texts)
        self.align = 'start'

        # Assign options
        self.n_lines = n_lines
        self.text_per_line = text_per_line

        # Set style
        self.predefined_style(style)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        for i in range(self.n_lines):
            format_font(self.latex_texts[i], font_family, font_size,
                        font_style, font_weight)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.1cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.1cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, n_lines, text_per_line):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        n_lines : `int`
            The number of lines of the text to be printed.
        text_per_line : `list` of length `n_lines`
            The text to be printed per line.
        """
        # Check if n_lines has changed
        if n_lines != self.n_lines:
            self.latex_texts = [ipywidgets.Latex(value=text_per_line[i])
                                for i in range(n_lines)]
            self.children = self.latex_texts
        else:
            for i in range(n_lines):
                self.latex_texts[i].value = text_per_line[i]
        self.n_lines = n_lines
        self.text_per_line = text_per_line


class RendererOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting rendering options. The widget consists of the
    following parts from `ipywidgets` and `menpowidgets.tools`:

    == ====================== =========================== ===================
    No Object                 Variable (`self.`)          Description
    == ====================== =========================== ===================
    1  Dropdown               `object_selection_dropdown` The object selector
    2  LineOptionsWidget      `options_widgets`           `list` with the

       MarkerOptionsWidget                                various rendering

       ImageOptionsWidget                                 sub-options widgets

       NumberingOptionsWidget

       FigureOptionsWidget

       LegendOptionsWidget

       GridOptionsWidget
    3  Tab                    `suboptions_tab`            Contains all 2
    == ====================== =========================== ===================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` methods.

    Parameters
    ----------
    renderer_options : `dict`
        The initial rendering options. For example
        ::

            lines_options = {'render_lines': True,
                             'line_width': 1,
                             'line_colour': ['b', 'r'],
                             'line_style': '-'}
            markers_options = {'render_markers': True,
                               'marker_size': 20,
                               'marker_face_colour': ['white', 'white'],
                               'marker_edge_colour': ['blue', 'red'],
                               'marker_style': 'o',
                               'marker_edge_width': 1}
            numbering_options = {'render_numbering': True,
                                 'numbers_font_name': 'serif',
                                 'numbers_font_size': 10,
                                 'numbers_font_style': 'normal',
                                 'numbers_font_weight': 'normal',
                                 'numbers_font_colour': ['black'],
                                 'numbers_horizontal_align': 'center',
                                 'numbers_vertical_align': 'bottom'}
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
            zoom_options = {'min': 0.1,
                            'max': 4.,
                            'step': 0.05,
                            'zoom': 1.}
            axes_options = {'render_axes': True,
                            'axes_font_name': 'serif',
                            'axes_font_size': 10,
                            'axes_font_style': 'normal',
                            'axes_font_weight': 'normal',
                            'axes_x_ticks': [0, 100],
                            'axes_y_ticks': None,
                            'axes_limits': {'x': None,
                                            'y': 0.1,
                                            'x_min': 0,
                                            'x_max': 100,
                                            'x_step': 1,
                                            'y_min': 0,
                                            'y_max': 100,
                                            'y_step': 1}}
            grid_options = {'render_grid': True,
                            'grid_line_style': '--',
                            'grid_line_width': 0.5}
            image_options = {'alpha': 1.,
                             'interpolation': 'bilinear',
                             'cmap_name': 'gray'}
            renderer_options = {'lines': lines_options,
                                'markers': markers_options,
                                'numbering': numbering_options,
                                'legend': legend_options,
                                'zoom': zoom_options,
                                'axes': axes_options,
                                'grid': grid_options,
                                'image': image_options}

    options_tabs : `list` of `str`
        `List` that defines the ordering of the options tabs. Possible values
        are

            ============= ========================
            Value         Returned class
            ============= ========================
            'lines'       `LineOptionsWidget`
            'markers'     `MarkerOptionsWidget`
            'numbering'   `NumberingOptionsWidget`
            'zoom_one'    `ZoomOneScaleWidget`
            'zoom_two'    `ZoomTwoScalesWidget`
            'legend'      `LegendOptionsWidget`
            'grid'        `GridOptionsWidget`
            'image'       `ImageOptionsWidget`
            'axes'        `AxesOptionsWidget`
            ============= ========================

    labels : `list` or ``None``, optional
        The `list` of labels employed by the `ColourSelectionWidget`.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    tabs_style : See Below, optional
        Sets a predefined style at the tabs of the widget. Possible options
        are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create a rendering options widget and then update its state. Firstly,
    we need to import it:

        >>> from menpowidgets.options import RendererOptionsWidget

    Let's set some initial options:

        >>> options_tabs = ['markers', 'lines', 'grid']
        >>> labels = ['jaw', 'eyes']

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected marker face colour and line
    width:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Marker face colour: {}, Line width: {}".format(
        >>>         wid.selected_values['markers']['marker_face_colour'],
        >>>         wid.selected_values['lines']['line_width'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> markers_options = {'render_markers': True, 'marker_size': 20,
        >>>                    'marker_face_colour': ['w', 'w'],
        >>>                    'marker_edge_colour': ['b', 'r'],
        >>>                    'marker_style': 'o', 'marker_edge_width': 1}
        >>> lines_options = {'render_lines': True, 'line_width': 1,
        >>>                  'line_colour': ['b', 'r'], 'line_style': '-'}
        >>> grid_options = {'render_grid': True, 'grid_line_style': '--',
        >>>                 'grid_line_width': 0.5}
        >>> rendering_options = {'lines': lines_options, 'grid': grid_options,
        >>>                      'markers': markers_options}
        >>>
        >>> # Create and display widget
        >>> wid = RendererOptionsWidget(rendering_options, options_tabs,
        >>>                             labels=labels,
        >>>                             render_function=render_function,
        >>>                             style='info')
        >>> wid

    By playing around, the printed message gets updated. The style of the widget
    can be changed as:

        >>> wid.predefined_style('minimal', 'info')

    Finally, let's change the widget status with a new dictionary of options:

        >>> markers_options = {'render_markers': False, 'marker_size': 20,
        >>>                    'marker_face_colour': ['k'],
        >>>                    'marker_edge_colour': ['c'],
        >>>                    'marker_style': 'o', 'marker_edge_width': 1}
        >>> lines_options = {'render_lines': False, 'line_width': 1,
        >>>                  'line_colour': ['r'], 'line_style': '-'}
        >>> grid_options = {'render_grid': True, 'grid_line_style': '--',
        >>>                 'grid_line_width': 0.5}
        >>> new_options = {'lines': lines_options, 'grid': grid_options,
        >>>                'markers': markers_options}
        >>>
        >>> # Set new labels
        >>> labels = ['1']
        >>>
        >>> # Update widget state
        >>> wid.set_widget_state(new_options, labels, allow_callback=True)
    """
    def __init__(self, renderer_options, options_tabs, labels=None,
                 render_function=None, style='minimal', tabs_style='minimal'):
        # Create children
        self.options_widgets = []
        self.tab_titles = []
        initial_dict = {}
        for o in options_tabs:
            if o == 'lines':
                self.options_widgets.append(LineOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render lines', labels=labels))
                self.tab_titles.append('Lines')
                initial_dict[o] = renderer_options[o]
            elif o == 'markers':
                self.options_widgets.append(MarkerOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render markers', labels=labels))
                self.tab_titles.append('Markers')
                initial_dict[o] = renderer_options[o]
            elif o == 'image':
                self.options_widgets.append(ImageOptionsWidget(
                    renderer_options[o], render_function=None))
                self.tab_titles.append('Image')
                initial_dict[o] = renderer_options[o]
            elif o == 'numbering':
                self.options_widgets.append(NumberingOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render numbering'))
                self.tab_titles.append('Numbering')
                initial_dict[o] = renderer_options[o]
            elif o == 'zoom':
                if isinstance(renderer_options[o]['zoom'], list):
                    self.options_widgets.append(ZoomTwoScalesWidget(
                        renderer_options[o], render_function=None,
                        description='Scale: ',
                        minus_description='fa-search-minus',
                        plus_description='fa-search-plus',
                        continuous_update=False))
                else:
                    self.options_widgets.append(ZoomOneScaleWidget(
                        renderer_options[o], render_function=None,
                        description='Scale: ',
                        minus_description='fa-search-minus',
                        plus_description='fa-search-plus',
                        continuous_update=False))
                self.tab_titles.append('Zoom')
                initial_dict['zoom'] = renderer_options[o]['zoom']
            elif o == 'axes':
                self.options_widgets.append(AxesOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render axes'))
                self.tab_titles.append('Axes')
                initial_dict[o] = {
                    'render_axes': renderer_options[o]['render_axes'],
                    'axes_font_name': renderer_options[o]['axes_font_name'],
                    'axes_font_size': renderer_options[o]['axes_font_size'],
                    'axes_font_style': renderer_options[o]['axes_font_style'],
                    'axes_font_weight': renderer_options[o]['axes_font_weight'],
                    'axes_x_ticks': renderer_options[o]['axes_x_ticks'],
                    'axes_y_ticks': renderer_options[o]['axes_y_ticks'],
                    'axes_x_limits': renderer_options[o]['axes_limits']['x'],
                    'axes_y_limits': renderer_options[o]['axes_limits']['y']}
            elif o == 'legend':
                self.options_widgets.append(LegendOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render legend'))
                self.tab_titles.append('Legend')
                initial_dict[o] = renderer_options[o]
            elif o == 'grid':
                self.options_widgets.append(GridOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render grid'))
                self.tab_titles.append('Grid')
                initial_dict[o] = renderer_options[o]
        self.suboptions_tab = ipywidgets.Tab(children=self.options_widgets)
        # set titles
        for (k, tl) in enumerate(self.tab_titles):
            self.suboptions_tab.set_title(k, tl)

        # Create final widget
        children = [self.suboptions_tab]
        super(RendererOptionsWidget, self).__init__(
            children, Dict, initial_dict, render_function=render_function,
            orientation='vertical', align='start')

        # Assign properties
        self.options_tabs = options_tabs
        self.labels = labels

        # Set style
        self.predefined_style(style, tabs_style)

        # Set functionality
        def save_options(name, value):
            self.selected_values = {o: self.options_widgets[i].selected_values
                                    for i, o in enumerate(options_tabs)}
        self._add_callback(save_options)

    def _add_callback(self, fun):
        for wid in self.options_widgets:
            wid.on_trait_change(fun, 'selected_values')

    def _remove_callback(self, fun):
        for wid in self.options_widgets:
            wid.on_trait_change(fun, 'selected_values', remove=True)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0,
              padding='0.2cm', margin=0, tabs_box_style=None,
              tabs_border_visible=True, tabs_border_colour='black',
              tabs_border_style='solid', tabs_border_width=1,
              tabs_border_radius=1, tabs_padding=0, tabs_margin=0,
              font_family='', font_size=None, font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
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
        tabs_box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        tabs_border_visible : `bool`, optional
            Defines whether to draw the border line around the tab widgets.
        tabs_border_colour : `str`, optional
            The color of the border around the tab widgets.
        tabs_border_style : `str`, optional
            The line style of the border around the tab widgets.
        tabs_border_width : `float`, optional
            The line width of the border around the tab widgets.
        tabs_border_radius : `float`, optional
            The radius of the corners of the box of the tab widgets.
        tabs_padding : `float`, optional
            The padding around the tab widgets.
        tabs_margin : `float`, optional
            The margin around the tab widgets.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        for wid in self.options_widgets:
            wid.style(box_style=tabs_box_style,
                      border_visible=tabs_border_visible,
                      border_colour=tabs_border_colour,
                      border_style=tabs_border_style,
                      border_width=tabs_border_width,
                      border_radius=tabs_border_radius, padding=tabs_padding,
                      margin=tabs_margin, font_family=font_family,
                      font_size=font_size, font_style=font_style,
                      font_weight=font_weight)
        format_font(self, font_family, font_size, font_style, font_weight)

    def predefined_style(self, style, tabs_style='minimal'):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================

        tabs_style : `str` (see below), optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if tabs_style == 'minimal' or tabs_style=='':
            tabs_style = ''
            tabs_border_visible = False
            tabs_border_colour = 'black'
            tabs_border_radius = 0
            tabs_padding = 0
        else:
            tabs_style = tabs_style
            tabs_border_visible = True
            tabs_border_colour = map_styles_to_hex_colours(tabs_style)
            tabs_border_radius = 10
            tabs_padding = '0.3cm'

        if style == 'minimal':
            self.style(box_style='', border_visible=True, border_colour='black',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.2cm', margin='0.5cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       tabs_box_style=tabs_style,
                       tabs_border_visible=tabs_border_visible,
                       tabs_border_colour=tabs_border_colour,
                       tabs_border_style='solid', tabs_border_width=1,
                       tabs_border_radius=tabs_border_radius,
                       tabs_padding=tabs_padding, tabs_margin='0.1cm')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.5cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       tabs_box_style=tabs_style,
                       tabs_border_visible=tabs_border_visible,
                       tabs_border_colour=tabs_border_colour,
                       tabs_border_style='solid', tabs_border_width=1,
                       tabs_border_radius=tabs_border_radius,
                       tabs_padding=tabs_padding, tabs_margin='0.1cm')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, renderer_options, labels, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.
        Note that the number of objects should not change.

        Parameters
        ----------
        renderer_options : `dict`
            The initial rendering options. For example
            ::

                lines_options = {'render_lines': True,
                                 'line_width': 1,
                                 'line_colour': ['b', 'r'],
                                 'line_style': '-'}
                markers_options = {'render_markers': True,
                                   'marker_size': 20,
                                   'marker_face_colour': ['white', 'white'],
                                   'marker_edge_colour': ['blue', 'red'],
                                   'marker_style': 'o',
                                   'marker_edge_width': 1}
                numbering_options = {'render_numbering': True,
                                     'numbers_font_name': 'serif',
                                     'numbers_font_size': 10,
                                     'numbers_font_style': 'normal',
                                     'numbers_font_weight': 'normal',
                                     'numbers_font_colour': ['black'],
                                     'numbers_horizontal_align': 'center',
                                     'numbers_vertical_align': 'bottom'}
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
                zoom_options = {'min': 0.1,
                                'max': 4.,
                                'step': 0.05,
                                'zoom': 1.}
                axes_options = {'render_axes': True,
                                'axes_font_name': 'serif',
                                'axes_font_size': 10,
                                'axes_font_style': 'normal',
                                'axes_font_weight': 'normal',
                                'axes_x_ticks': [0, 100],
                                'axes_y_ticks': None,
                                'axes_limits': {'x': None,
                                                'y': 0.1,
                                                'x_min': 0,
                                                'x_max': 100,
                                                'x_step': 1,
                                                'y_min': 0,
                                                'y_max': 100,
                                                'y_step': 1}}
                grid_options = {'render_grid': True,
                                'grid_line_style': '--',
                                'grid_line_width': 0.5}
                image_options = {'alpha': 1.,
                                 'interpolation': 'bilinear',
                                 'cmap_name': 'gray'}
                renderer_options = {'lines': lines_options,
                                    'markers': markers_options,
                                    'numbering': numbering_options,
                                    'legend': legend_options,
                                    'zoom': zoom_options,
                                    'axes': axes_options,
                                    'grid': grid_options,
                                    'image': image_options}

        labels : `list` or ``None``, optional
            The `list` of labels employed by the `ColourSelectionWidget`.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Update sub-options widgets
        for i, tab in enumerate(self.options_tabs):
            if tab == 'lines' or tab == 'markers':
                self.options_widgets[i].set_widget_state(
                    renderer_options[tab], labels=labels, allow_callback=False)
            else:
                self.options_widgets[i].set_widget_state(
                    renderer_options[tab], allow_callback=False)

        # Assign properties
        self.labels = labels

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class SaveFigureOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for saving a figure to file. The widget consists of the
    following parts from `IPython.html.widgets` and
    `menpowidgets.tools`:

    == ===================== ====================== ==========================
    No Object                Variable (`self.`)     Description
    == ===================== ====================== ==========================
    1  Select                `file_format_select`   Image format selector
    2  FloatText             `dpi_text`             DPI selector
    3  Dropdown              `orientation_dropdown` Paper orientation selector
    4  Select                `papertype_select`     Paper type selector
    5  Checkbox              `transparent_checkbox` Transparency setter
    6  ColourSelectionWidget `facecolour_widget`    Face colour selector
    7  ColourSelectionWidget `edgecolour_widget`    Edge colour selector
    8  FloatText             `pad_inches_text`      Padding in inches setter
    9  Text                  `filename_text`        Path and filename
    10 Checkbox              `overwrite_checkbox`   Overwrite flag
    11 Latex                 `error_latex`          Error message area
    12 Button                `save_button`          Save button
    13 VBox                  `path_box`             Contains 9, 1, 10, 4
    14 VBox                  `page_box`             Contains 3, 2, 8
    15 VBox                  `colour_box`           Contains 6, 7, 5
    16 Tab                   `options_tabs`         Contains 13, 14, 15
    17 HBox                  `save_box`             Contains 12, 11
    18 VBox                  `options_box`          Contains 16, 17
    == ===================== ====================== ==========================

    To set the styling please refer to the ``style()`` and
    ``predefined_style()`` methods.

    Parameters
    ----------
    renderer : :map:`Renderer` class or subclass
        The renderer object that was used to render the figure.
    file_format : `str`, optional
        The initial value of the file format.
    dpi : `float` or ``None``, optional
        The initial value of the dpi. If ``None``, then dpi is set to ``0``.
    orientation : {``'portrait'``, ``'landscape'``}, optional
        The initial value of the orientation.
    papertype : `str`, optional
        The initial value of the paper type.
        Possible options are ::

            {'letter', 'legal', 'executive', 'ledger', 'a0', 'a1', 'a2', 'a3',
             'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'b0', 'b1', 'b2', 'b3',
             'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10'}

    transparent : `bool`, optional
        The initial value of the transparency flag.
    facecolour : `str` or `list` of `float`, optional
        The initial value of the face colour.
    edgecolour : `str` or `list` of `float`, optional
        The initial value of the edge colour.
    pad_inches : `float`, optional
        The initial value of the figure padding in inches.
    overwrite : `bool`, optional
        The initial value of the overwrite flag.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================
    """
    def __init__(self, renderer, file_format='png', dpi=None,
                 orientation='portrait', papertype='letter', transparent=False,
                 facecolour='white', edgecolour='white', pad_inches=0.,
                 overwrite=False, style='minimal'):
        from os import getcwd
        from os.path import join, splitext

        # Create widgets
        file_format_dict = OrderedDict()
        file_format_dict['png'] = 'png'
        file_format_dict['jpg'] = 'jpg'
        file_format_dict['pdf'] = 'pdf'
        file_format_dict['eps'] = 'eps'
        file_format_dict['postscript'] = 'ps'
        file_format_dict['svg'] = 'svg'
        self.file_format_select = ipywidgets.Select(
            options=file_format_dict, value=file_format, description='Format',
            width='3cm')
        if dpi is None:
            dpi = 0
        self.dpi_text = ipywidgets.FloatText(description='DPI', value=dpi,
                                             min=0.)
        orientation_dict = OrderedDict()
        orientation_dict['portrait'] = 'portrait'
        orientation_dict['landscape'] = 'landscape'
        self.orientation_dropdown = ipywidgets.Dropdown(
            options=orientation_dict, value=orientation,
            description='Orientation')
        papertype_dict = OrderedDict()
        papertype_dict['letter'] = 'letter'
        papertype_dict['legal'] = 'legal'
        papertype_dict['executive'] = 'executive'
        papertype_dict['ledger'] = 'ledger'
        papertype_dict['a0'] = 'a0'
        papertype_dict['a1'] = 'a1'
        papertype_dict['a2'] = 'a2'
        papertype_dict['a3'] = 'a3'
        papertype_dict['a4'] = 'a4'
        papertype_dict['a5'] = 'a5'
        papertype_dict['a6'] = 'a6'
        papertype_dict['a7'] = 'a7'
        papertype_dict['a8'] = 'a8'
        papertype_dict['a9'] = 'a9'
        papertype_dict['a10'] = 'a10'
        papertype_dict['b0'] = 'b0'
        papertype_dict['b1'] = 'b1'
        papertype_dict['b2'] = 'b2'
        papertype_dict['b3'] = 'b3'
        papertype_dict['b4'] = 'b4'
        papertype_dict['b5'] = 'b5'
        papertype_dict['b6'] = 'b6'
        papertype_dict['b7'] = 'b7'
        papertype_dict['b8'] = 'b8'
        papertype_dict['b9'] = 'b9'
        papertype_dict['b10'] = 'b10'
        self.papertype_select = ipywidgets.Select(
            options=papertype_dict, value=papertype, description='Paper type',
            visible=file_format == 'ps', width='3cm')
        self.transparent_checkbox = ipywidgets.Checkbox(
            description='Transparent', value=transparent)
        self.facecolour_widget = ColourSelectionWidget(
            [facecolour], render_function=None, description='Face colour')
        self.edgecolour_widget = ColourSelectionWidget(
            [edgecolour], render_function=None, description='Edge colour')
        self.pad_inches_text = ipywidgets.FloatText(description='Pad (inch)',
                                                    value=pad_inches)
        self.filename_text = ipywidgets.Text(
            description='Path', value=join(getcwd(), 'Untitled.' + file_format),
            width='10cm')
        self.overwrite_checkbox = ipywidgets.Checkbox(
            description='Overwrite if file exists', value=overwrite)
        self.error_latex = ipywidgets.Latex(value="", font_weight='bold',
                                            font_style='italic')
        self.save_button = ipywidgets.Button(description='  Save',
                                             icon='fa-floppy-o', margin='0.2cm')

        # Group widgets
        self.path_box = ipywidgets.VBox(
            children=[self.filename_text, self.file_format_select,
                      self.papertype_select, self.overwrite_checkbox],
            align='end', margin='0.2cm')
        self.page_box = ipywidgets.VBox(
            children=[self.orientation_dropdown, self.dpi_text,
                      self.pad_inches_text], margin='0.2cm')
        self.colour_box = ipywidgets.VBox(
            children=[self.facecolour_widget, self.edgecolour_widget,
                      self.transparent_checkbox], margin='0.2cm')
        self.options_tabs = ipywidgets.Tab(
            children=[self.path_box, self.page_box, self.colour_box],
            margin=0, padding='0.1cm')
        self.options_tabs_box = ipywidgets.VBox(
            children=[self.options_tabs], border_width=1, border_color='black',
            margin='0.3cm', padding='0.2cm')
        tab_titles = ['Path', 'Page setup', 'Image colour']
        for (k, tl) in enumerate(tab_titles):
            self.options_tabs.set_title(k, tl)
        self.save_box = ipywidgets.HBox(
            children=[self.save_button, self.error_latex], align='center')
        self.options_box = ipywidgets.VBox(
            children=[self.options_tabs, self.save_box], align='center')
        super(SaveFigureOptionsWidget, self).__init__(
            children=[self.options_box])
        self.align = 'start'

        # Assign renderer
        self.renderer = renderer

        # Set style
        self.predefined_style(style)

        # Set functionality
        def papertype_visibility(name, value):
            self.papertype_select.visible = value == 'ps'
        self.file_format_select.on_trait_change(papertype_visibility, 'value')

        def set_extension(name, value):
            file_name, file_extension = splitext(self.filename_text.value)
            self.filename_text.value = file_name + '.' + value
        self.file_format_select.on_trait_change(set_extension, 'value')

        def save_function(name):
            # set save button state
            self.error_latex.value = ''
            self.save_button.description = 'Saving...'
            self.save_button.disabled = True

            # save figure
            selected_dpi = self.dpi_text.value
            if self.dpi_text.value == 0:
                selected_dpi = None
            try:
                self.renderer.save_figure(
                    filename=self.filename_text.value, dpi=selected_dpi,
                    face_colour=
                    self.facecolour_widget.selected_values[0],
                    edge_colour=
                    self.edgecolour_widget.selected_values[0],
                    orientation=self.orientation_dropdown.value,
                    paper_type=self.papertype_select.value,
                    format=self.file_format_select.value,
                    transparent=self.transparent_checkbox.value,
                    pad_inches=self.pad_inches_text.value,
                    overwrite=self.overwrite_checkbox.value)
                self.error_latex.value = ''
            except ValueError as e:
                if (e.message == 'File already exists. Please set the '
                                 'overwrite kwarg if you wish to overwrite '
                                 'the file.'):
                    self.error_latex.value = 'File exists! ' \
                                             'Tick overwrite to replace it.'
                else:
                    self.error_latex.value = e.message

            # set save button state
            self.save_button.description = 'Save'
            self.save_button.disabled = False
        self.save_button.on_click(save_function)

    def style(self, box_style=None, border_visible=False, border_color='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_color : `str`, optional
            The color of the border around the widget.
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

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_color, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.file_format_select, font_family, font_size, font_style,
                    font_weight)
        format_font(self.dpi_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.orientation_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.papertype_select, font_family, font_size,  font_style,
                    font_weight)
        format_font(self.transparent_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.pad_inches_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.filename_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.overwrite_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.save_button, font_family, font_size, font_style,
                    font_weight)
        self.facecolour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        self.edgecolour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style='', border_visible=True, border_color='black',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
            self.save_button.button_style = ''
            self.save_button.font_weight = 'normal'
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_color= map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
            self.save_button.button_style = 'primary'
            self.save_button.font_weight = 'bold'
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')
